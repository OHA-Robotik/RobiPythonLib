import time

from Robi42Lib.robi42 import Robi42
from machine import Timer

FWD = True
BWD = not FWD


class RobiConfig:
    wheel_radius: float  # m
    track_width: (
        float  # The distance between the center lines of the two wheels. Unit: m
    )

    def __init__(self, wheel_radius: float, track_width: float):
        self.wheel_radius = wheel_radius
        self.track_width = track_width


class WaypointMission:
    STOP_TIME = 0.1  # s

    def __init__(self, robi: Robi42, robi_config: RobiConfig):
        self.robi_config = robi_config
        self.robi = robi
        self.robi.motors.set_stepping_size(True, True, True)

    def _set_velocity(self, velocity: float):
        self.robi.motors.set_velocity(velocity)

    def _set_velocity_left(self, velocity: float):
        self.robi.motors.left.set_velocity(velocity, self.robi_config.wheel_radius)

    def _set_velocity_right(self, velocity: float):
        self.robi.motors.right.set_velocity(velocity, self.robi_config.wheel_radius)

    def turn(
        self,
        *,
        left: bool,
        total_turn_degree: float,
        acceleration_degree: float,
        deceleration_degree: float,
        inner_radius: float,
        acceleration: float,
        initial_velocity: float,
    ):
        k = inner_radius / (inner_radius + self.robi_config.track_width)

        if left:
            right_velocity = initial_velocity
            left_velocity = right_velocity * k

            right_dv = acceleration * 0.1
            left_dv = right_dv * k
        else:
            left_velocity = initial_velocity
            right_velocity = left_velocity * k

            left_dv = acceleration * 0.1
            right_dv = left_dv * k

        timer = Timer(-1)

        self.robi.motors.set_direction(FWD)
        start_rot = self.robi.gyro.z_rot

        def timer_callback(ti: Timer):

            nonlocal left_velocity, right_velocity

            left_velocity += left_dv
            right_velocity += right_dv

            self._set_velocity_left(left_velocity)
            self._set_velocity_right(right_velocity)

        timer.init(period=100, callback=timer_callback)

        while abs(self.robi.gyro.z_rot - start_rot) < acceleration_degree:
            time.sleep_ms(10)

        left_dv = right_dv = 0

        while (
            abs(self.robi.gyro.z_rot - start_rot)
            < total_turn_degree - deceleration_degree
        ):
            time.sleep_ms(10)

        if left:
            right_dv = -acceleration * 0.1
            left_dv = right_dv * k
        else:
            left_dv = -acceleration * 0.1
            right_dv = left_dv * k

        outer_velocity = right_velocity if left else left_velocity
        while (
            abs(self.robi.gyro.z_rot - start_rot) < total_turn_degree
            and outer_velocity > 0
        ):
            time.sleep_ms(10)

        timer.deinit()

    def rapid_turn(
        self,
        left: bool,
        total_turn_degree: float,
        acceleration_degree: float,
        acceleration: float,
    ):
        v = 0
        dv = acceleration * 0.1
        timer = Timer(-1)
        start_rot = self.robi.gyro.z_rot

        if left:
            self.robi.motors.left.set_direction(BWD)
            self.robi.motors.right.set_direction(FWD)
        else:
            self.robi.motors.left.set_direction(FWD)
            self.robi.motors.right.set_direction(BWD)

        def timer_callback(ti: Timer):
            nonlocal v
            v += dv
            self._set_velocity(v)

        timer.init(period=100, callback=timer_callback)

        while abs(self.robi.gyro.z_rot - start_rot) < acceleration_degree:
            time.sleep_ms(10)

        dv = 0

        while (
            abs(self.robi.gyro.z_rot - start_rot)
            < total_turn_degree - acceleration_degree
        ):
            time.sleep_ms(10)

        dv = -acceleration * 0.1

        while abs(self.robi.gyro.z_rot - start_rot) < total_turn_degree and v > 0:
            time.sleep_ms(10)

        timer.deinit()

    def _accelerate(
        self,
        *,
        acceleration: float,
        initial_velocity: float,
        acceleration_time: float,
    ):
        v = initial_velocity
        dv = acceleration * 0.1
        timer = Timer(-1)
        start_rot = self.robi.gyro.z_rot

        def timer_callback(ti: Timer):
            nonlocal v

            v += dv

            rot = self.robi.gyro.z_rot - start_rot
            compensation = rot * v * 0.02

            self._set_velocity_left(v + compensation)
            self._set_velocity_right(v - compensation)

        timer.init(period=100, callback=timer_callback)

        time.sleep(acceleration_time)

        timer.deinit()

    def drive(
        self,
        *,
        acceleration: float,
        initial_velocity: float,
        constant_speed_time: float,
        acceleration_time: float,
        deceleration_time: float,
    ):

        max_velocity = acceleration * acceleration_time

        self.robi.motors.set_direction(FWD)

        self._accelerate(
            acceleration=acceleration,
            initial_velocity=initial_velocity,
            acceleration_time=acceleration_time,
        )

        timer = Timer(-1)
        start_rot = self.robi.gyro.z_rot

        def timer_callback(ti: Timer):
            rot = self.robi.gyro.z_rot - start_rot
            compensation = rot * max_velocity * 0.02
            self._set_velocity_left(max_velocity + compensation)
            self._set_velocity_right(max_velocity - compensation)

        timer.init(period=10, callback=timer_callback)

        time.sleep(constant_speed_time - 0.1)

        timer.deinit()

        self._accelerate(
            acceleration=-acceleration,
            initial_velocity=max_velocity,
            acceleration_time=deceleration_time,
        )

    def calibrate_gyro(self):
        self.robi.gyro.calibrate_offsets(5000)
        self.robi.gyro.start()


def main():
    robi = Robi42()

    rc = RobiConfig(wheel_radius=0.032, track_width=0.155)
    wm = WaypointMission(robi, rc)

    print("Calibrating Gyro...", end=" ")
    wm.calibrate_gyro()
    print("Done")

    robi.motors.enable()

    wm.drive(
        acceleration=0.3,
        initial_velocity=0,
        acceleration_time=1.7,
        deceleration_time=0,
        constant_speed_time=1.11,
    )

    wm.turn(
        left=True,
        total_turn_degree=90,
        inner_radius=0.5,
        acceleration=0.2,
        initial_velocity=0.51,
        acceleration_degree=0,
        deceleration_degree=56.7,
    )

    wm.rapid_turn(
        left=False,
        total_turn_degree=180,
        acceleration_degree=45,
        acceleration=0.1,
    )

    wm.drive(
        acceleration=0.6,
        initial_velocity=0,
        acceleration_time=1,
        deceleration_time=1,
        constant_speed_time=0.7,
    )

    robi.motors.disable()


if __name__ == "__main__":
    main()
