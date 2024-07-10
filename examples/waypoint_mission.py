import json
import math

from machine import Pin, I2C

from Robi42Lib.device_drivers.impl.mpu6050 import bytes_toint
from Robi42Lib.robi42 import Robi42

FWD = False
BWD = True


class Gyro:
    run = True
    z_cal = 0

    def __init__(self) -> None:
        self.i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
        self.i2c.writeto_mem(0x68, 0x6B, bytes(1))  # Set SLEEP reg to 1
        self.i2c.writeto_mem(0x68, 0x1B, bytes(0))  # Set Gyro range

    def z(self):
        raw_data = self.i2c.readfrom_mem(0x68, 0x47, 2)
        return bytes_toint(raw_data[0], raw_data[1]) / 131 - self.z_cal

    def calibrate(self, iterations=10000):
        z_sum = 0
        for _ in range(iterations):
            z_sum += self.z()
        self.z_cal = z_sum / iterations


class RobiConfig:
    wheel_radius: float  # m
    track_width: (
        float  # The distance between the center lines of the two wheels. Unit: m
    )

    def __init__(self, wheel_radius: float, track_width: float):
        self.wheel_radius = wheel_radius
        self.track_width = track_width


class MissionInstruction: ...


class DriveInstruction(MissionInstruction):
    def __init__(self, distance: float, target_velocity: float, acceleration: float):
        self.distance = distance
        self.target_velocity = target_velocity
        self.acceleration = acceleration

        if acceleration != 0:
            self.acceleration_time = target_velocity / acceleration
            self.acceleration_distance = 0.5 * acceleration * self.acceleration_time**2


class TurnInstruction(MissionInstruction):
    def __init__(self, left: bool, turn_degree: float, radius: float):
        self.left = left
        self.turn_degree = turn_degree
        self.radius = radius


class InstructionResult:
    def __init__(self, managed_velocity: float, covered_distance: float):
        self.managed_velocity = managed_velocity
        self.covered_distance = covered_distance


class Importer:
    @staticmethod
    def decode(json_string: str) -> tuple[RobiConfig, list[MissionInstruction]]:
        data = json.loads(json_string)
        return RobiConfig(
            data["config"]["wheel_radius"], data["config"]["track_width"]
        ), [
            (
                DriveInstruction(
                    instruction["distance"],
                    instruction["target_velocity"],
                    instruction["acceleration"],
                )
                if instruction["type"] == "drive"
                else TurnInstruction(
                    instruction["left"],
                    instruction["turn_degree"],
                    instruction["radius"],
                )
            )
            for instruction in data["instructions"]
        ]


class WaypointMission:
    STOP_TIME = 0.1  # s

    def __init__(
        self,
        robi: Robi42,
        robi_config: RobiConfig,
        instructions: list[MissionInstruction],
    ) -> None:
        self.instructions = instructions
        self.robi_config = robi_config
        self.robi = robi
        self.robi.motors.set_stepping_size(True, True, True)
        self.gyro = Gyro()
        self.last_inst_was_turn = False

    def turn(
        self,
        *,
        prev_inst_result: InstructionResult,
        turn_instruction: TurnInstruction,
        prev_instruction: MissionInstruction,
    ):
        wr = self.robi_config.wheel_radius
        turn_degree_rad = turn_instruction.turn_degree * (math.pi / 180)

        outer_distance = turn_degree_rad * (
            turn_instruction.radius + self.robi_config.track_width
        )
        inner_distance = turn_degree_rad * turn_instruction.radius

        if (
            isinstance(prev_instruction, TurnInstruction)
            and prev_instruction.left == turn_instruction.left
        ):
            inner_velocity = prev_inst_result.managed_velocity
            time_for_completion = inner_distance / inner_velocity
            outer_velocity = outer_distance / time_for_completion
        else:
            outer_velocity = prev_inst_result.managed_velocity
            time_for_completion = outer_distance / outer_velocity
            inner_velocity = inner_distance / time_for_completion

        if turn_instruction.left:
            self.robi.motors.left.set_velocity(inner_velocity, wr)
            self.robi.motors.right.set_velocity(outer_velocity, wr)
        else:
            self.robi.motors.right.set_velocity(inner_velocity, wr)
            self.robi.motors.left.set_velocity(outer_velocity, wr)

        rotation = 0

        while rotation < turn_instruction.turn_degree:
            rotation += abs(self.gyro.z()) * 0.003  # s Exakt ausprobiert

        return InstructionResult(inner_velocity, 0)

    def accelerate(self, a: float, from_v: float, to_v: float, s_limit: float = 1000):

        wr = self.robi_config.wheel_radius

        decel = a < 0

        v = from_v  # m/s
        s = 0  # m
        dt = 0.0015  # s, TODO: Calibrate this value
        rot = 0  # °

        # start = time.time_ns()
        while (((not decel) and v < to_v) or (decel and v > to_v)) and s < s_limit:
            rot += self.gyro.z() * dt
            ausgleich = abs(rot * (v / 50))
            if rot > 0:
                self.robi.motors.left.set_velocity(v - ausgleich, wr)
                self.robi.motors.right.set_velocity(v + ausgleich, wr)
            else:
                self.robi.motors.left.set_velocity(v + ausgleich, wr)
                self.robi.motors.right.set_velocity(v - ausgleich, wr)
            v += dt * a
            s += dt * v

        # end = time.time_ns()
        # print("Actual time:", (end-start) / 1e6, "ms")

        if v < 0:
            v = 0
        if s < 0:
            s = 0

        return InstructionResult(v, s)

    def drive(self, prev_inst_result: InstructionResult, instruction: DriveInstruction):

        wr = self.robi_config.wheel_radius

        self.robi.motors.set_direction(FWD)

        acceleration_result = self.accelerate(
            instruction.acceleration,
            prev_inst_result.managed_velocity,
            instruction.target_velocity,
            instruction.distance,
        )

        if acceleration_result.managed_velocity <= 0:
            return InstructionResult(0, acceleration_result.covered_distance)

        rot = 0
        s = 0
        dt = 0.0013  # TODO: Calibrate this value
        distance_to_drive = instruction.distance - acceleration_result.covered_distance
        # start = time.time_ns()

        while s < distance_to_drive:
            rot += self.gyro.z() * dt
            ausgleich = abs(rot * (acceleration_result.managed_velocity / 50))
            if rot > 0:
                self.robi.motors.left.set_velocity(
                    acceleration_result.managed_velocity - ausgleich, wr
                )
                self.robi.motors.right.set_velocity(
                    acceleration_result.managed_velocity + ausgleich, wr
                )
            else:
                self.robi.motors.left.set_velocity(
                    acceleration_result.managed_velocity + ausgleich, wr
                )
                self.robi.motors.right.set_velocity(
                    acceleration_result.managed_velocity - ausgleich, wr
                )
            s += acceleration_result.managed_velocity * dt

        # end = time.time_ns()
        # print("Actual time:", (end - start) / 1e9, "Should time:", distance_to_drive / managed_velocity)

        return InstructionResult(
            acceleration_result.managed_velocity,
            s + acceleration_result.covered_distance,
        )

    def run_instruction(
        self,
        *,
        prev_inst_result: InstructionResult,
        prev_instruction: MissionInstruction,
        instruction: MissionInstruction,
    ):
        if isinstance(instruction, DriveInstruction):
            res = self.drive(prev_inst_result, instruction)
            self.last_inst_was_turn = False
        elif isinstance(instruction, TurnInstruction):
            res = self.turn(
                prev_inst_result=prev_inst_result,
                prev_instruction=prev_instruction,
                turn_instruction=instruction,
            )
            self.last_inst_was_turn = True
        else:
            raise NotImplemented()
        return res

    def start(self):
        self.gyro.calibrate()

        prev_inst_result = InstructionResult(0, 0)
        prev_inst = DriveInstruction(0, 0, 0)
        for instruction in self.instructions:
            prev_inst_result = self.run_instruction(
                prev_inst_result=prev_inst_result,
                instruction=instruction,
                prev_instruction=prev_inst,
            )
            prev_inst = instruction

        self.robi.motors.disable()


PATH1 = [
    DriveInstruction(0.5, 0.5, 0.4),
    DriveInstruction(0.2, 0.3, 0.4),
    TurnInstruction(True, 90, 0.1),
    TurnInstruction(False, 180, 0.3),
    DriveInstruction(0.5, 0.5, 0.4),
    DriveInstruction(0.2, 0.3, 0.4),
    TurnInstruction(False, 90, 0.1),
    DriveInstruction(1, 0.6, 0.4),
]


def main(robi: Robi42):

    with open("/examples/exported_waypoint_mission.json") as f:
        data = f.read()

    decoded = Importer.decode(data)
    wm = WaypointMission(robi, decoded[0], decoded[1])

    print("Start")
    wm.start()


if __name__ == "__main__":
    main(Robi42())
