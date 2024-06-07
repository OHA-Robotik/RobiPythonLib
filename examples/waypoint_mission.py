from Robi42Lib.robi42 import Robi42
from machine import Pin, I2C
from Robi42Lib.device_drivers.impl.mpu6050 import bytes_toint
import time
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
    track_width: float  # The distance between the center lines of the two wheels. Unit: m

    def __init__(self, wheel_radius: float, track_width: float):
        self.wheel_radius = wheel_radius
        self.track_width = track_width


class MissionInstruction:
    def __init__(
            self,
            rotation: float,
            distance: float,
            target_velocity: float,
            acceleration: float,
    ):
        self.rotation = rotation
        self.distance = distance
        self.target_velocity = target_velocity
        self.acceleration = acceleration

        if acceleration != 0:
            self.acceleration_time = target_velocity / acceleration
            self.acceleration_distance = 0.5 * acceleration * self.acceleration_time ** 2


class WaypointMission:
    STOP_TIME = 0.1  # s
    ROT_SPEED = 0.075  # m/s

    def __init__(self, robi: Robi42, robi_config: RobiConfig, instructions: list[MissionInstruction]) -> None:
        self.instructions = instructions
        self.robi_config = robi_config
        self.robi = robi
        self.robi.motors.set_stepping_size(True, True, True)
        self.gyro = Gyro()

    def turn(self, degrees: float):
        if degrees == 0:
            return

        self.set_v(self.ROT_SPEED)
        rotation = 0

        left = degrees < 0
        self.robi.motors.right.set_direction(not left)
        self.robi.motors.left.set_direction(left)

        DT = 0.0002475  # m Exakt ausprobiert
        if left:
            while rotation > degrees:
                rotation += self.gyro.z() * DT
        else:
            while rotation < degrees:
                rotation += self.gyro.z() * DT

    def set_v(self, v: float, left=True, right=True):
        f = int(v / (1.8 / 32 * (math.pi / 180) * self.robi_config.wheel_radius))

        if f < 7:
            self.robi.motors.disable()
        else:
            self.robi.motors.enable()
            if left:
                self.robi.motors.left.set_freq(f)
            if right:
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
                self.set_v(v - ausgleich, True, False)
                self.set_v(v + ausgleich, False, True)
            else:
                self.set_v(v + ausgleich, True, False)
                self.set_v(v - ausgleich, False, True)
            v += dt * a
            s += dt * v

        # end = time.time_ns()
        # print("Actual time:", (end-start) / 1e6, "ms")

        return v, s

    def drive(self, instruction: MissionInstruction):

        self.robi.motors.set_direction(FWD)

        managed_velocity, covered_distance = self.accelerate(
            instruction.acceleration,
            self.ROT_SPEED,
            instruction.target_velocity,
            instruction.distance / 2,
        )

        rot = 0
        s = 0
        dt = 0.001907
        distance_to_drive = instruction.distance - covered_distance * 2
        # start = time.time_ns()

        while s < distance_to_drive:
            rot += self.gyro.z() * dt
            ausgleich = abs(rot * (managed_velocity / 50))
            if rot > 0:
                self.set_v(managed_velocity - ausgleich, True, False)
                self.set_v(managed_velocity + ausgleich, False, True)
            else:
                self.set_v(managed_velocity + ausgleich, True, False)
                self.set_v(managed_velocity - ausgleich, False, True)
            s += managed_velocity * dt

        # end = time.time_ns()
        # print("Actual time:", (end - start) / 1e9, "Should time:", distance_to_drive / managed_velocity)

        self.accelerate(
            -instruction.acceleration,
            managed_velocity,
            0,
            instruction.distance / 2,
        )

    def start(self):
        self.gyro.calibrate()

        for instruction in self.instructions:
            time.sleep(self.STOP_TIME)
            self.turn(instruction.rotation)
            self.drive(instruction)
            self.robi.motors.disable()

        self.robi.motors.disable()


PATH1 = [MissionInstruction(0, 5, 2, 0.2)]

PATH2 = [
            MissionInstruction(0, 2, 1, 0.01),
        ] + [
            MissionInstruction(180, 2, 1, 0.5),
            MissionInstruction(180, 2, 1, 0.5),
        ] * 5


def main():
    r = Robi42()
    config = RobiConfig(0.035, 0.147)
    wm = WaypointMission(r, config, PATH1)
    wm.start()


if __name__ == "__main__":
    main()
