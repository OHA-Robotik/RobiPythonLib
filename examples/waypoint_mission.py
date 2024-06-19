import json

from Robi42Lib.robi42 import Robi42
from machine import Pin, I2C
from Robi42Lib.device_drivers.impl.mpu6050 import bytes_toint
import math

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

    def turn(
        self, prev_inst_result: InstructionResult, turn_instruction: TurnInstruction
    ):
        turn_degree_rad = turn_instruction.turn_degree * (math.pi / 180)

        outer_distance = turn_degree_rad * (
            turn_instruction.radius + self.robi_config.track_width
        )
        median_distance = turn_degree_rad * (
            turn_instruction.radius + self.robi_config.track_width / 2
        )
        inner_distance = turn_degree_rad * turn_instruction.radius

        time_for_completion = median_distance / prev_inst_result.managed_velocity

        inner_velocity = inner_distance / time_for_completion
        outer_velocity = outer_distance / time_for_completion

        if turn_instruction.left:
            self.set_v(inner_velocity, right=False)
            self.set_v(outer_velocity, left=False)
        else:
            self.set_v(inner_velocity, left=False)
            self.set_v(outer_velocity, right=False)

        rotation = 0

        while rotation < turn_instruction.turn_degree:
            rotation += abs(self.gyro.z()) * 0.003  # s Exakt ausprobiert

        return InstructionResult(prev_inst_result.managed_velocity, 0)

    def set_v(self, v: float, left=True, right=True):
        f = int(v / (1.8 / 32 * (math.pi / 180) * self.robi_config.wheel_radius))

        if left:
            if f < 7:
                self.robi.motors.left.disable()
                return
            self.robi.motors.left.enable()
            self.robi.motors.left.set_freq(f)
        if right:
            if f < 7:
                self.robi.motors.right.disable()
                return
            self.robi.motors.right.enable()
            self.robi.motors.right.set_freq(f)

    def accelerate(self, a: float, from_v: float, to_v: float, s_limit: float = 1000):

        decel = a < 0

        v = from_v  # m/s
        s = 0  # m
        dt = 0.002  # s
        rot = 0  # °

        # start = time.time_ns()
        while (((not decel) and v < to_v) or (decel and v > to_v)) and s < s_limit:
            rot += self.gyro.z() * dt
            ausgleich = abs(rot * (v / 50))
            if rot > 0:
                self.set_v(v - ausgleich, right=False)
                self.set_v(v + ausgleich, left=False)
            else:
                self.set_v(v + ausgleich, right=False)
                self.set_v(v - ausgleich, left=False)
            v += dt * a
            s += dt * v

        # end = time.time_ns()
        # print("Actual time:", (end-start) / 1e6, "ms")

        return InstructionResult(v, s)

    def drive(self, prev_inst_result: InstructionResult, instruction: DriveInstruction):

        self.robi.motors.set_direction(FWD)

        decel = prev_inst_result.managed_velocity > instruction.target_velocity

        acceleration_result = self.accelerate(
            -instruction.acceleration if decel else instruction.acceleration,
            prev_inst_result.managed_velocity,
            instruction.target_velocity,
            instruction.distance,
        )

        rot = 0
        s = 0
        dt = 0.001907
        distance_to_drive = instruction.distance - acceleration_result.covered_distance
        # start = time.time_ns()

        while s < distance_to_drive:
            rot += self.gyro.z() * dt
            ausgleich = abs(rot * (acceleration_result.managed_velocity / 50))
            if rot > 0:
                self.set_v(
                    acceleration_result.managed_velocity - ausgleich, True, False
                )
                self.set_v(
                    acceleration_result.managed_velocity + ausgleich, False, True
                )
            else:
                self.set_v(
                    acceleration_result.managed_velocity + ausgleich, True, False
                )
                self.set_v(
                    acceleration_result.managed_velocity - ausgleich, False, True
                )
            s += acceleration_result.managed_velocity * dt

        # end = time.time_ns()
        # print("Actual time:", (end - start) / 1e9, "Should time:", distance_to_drive / managed_velocity)

        return InstructionResult(
            acceleration_result.managed_velocity,
            s + acceleration_result.covered_distance,
        )

    def run_instruction(
        self, prev_inst_result: InstructionResult, instruction: MissionInstruction
    ):
        if isinstance(instruction, DriveInstruction):
            return self.drive(prev_inst_result, instruction)
        if isinstance(instruction, TurnInstruction):
            return self.turn(prev_inst_result, instruction)
        raise NotImplemented()

    def start(self):
        self.gyro.calibrate()

        prev_inst_result = InstructionResult(0, 0)
        for instruction in self.instructions:
            prev_inst_result = self.run_instruction(prev_inst_result, instruction)

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


def main():
    r = Robi42()

    with open("/examples/exported_waypoint_mission.json") as f:
        data = f.read()

    decoded = Importer.decode(data)
    wm = WaypointMission(r, decoded[0], decoded[1])

    print("Start")
    wm.start()


if __name__ == "__main__":
    main()
