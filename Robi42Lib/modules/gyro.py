from math import pi

from machine import Pin, I2C, Timer
import time


def bytes_to_int(high, low):
    value = (high << 8) | low
    if value & 0x8000:  # if the sign bit is set
        value -= 0x10000
    return value


GYRO_RANGE_BYTES = (0, 0x8, 0x10, 0x18)
GYRO_RANGE_SCALE = (131, 65.5, 32.8, 16.4)


class Gyro:

    def __init__(self, gyro_range: int = 0, timer_period_ms: int = 10) -> None:
        """
        gyro_range:
        Value:              0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        """

        self._gyro_range = gyro_range
        self._timer_period = timer_period_ms / 1000

        self._gyro_scale = GYRO_RANGE_SCALE[self._gyro_range]

        self._x_rot = 0
        self._y_rot = 0
        self._z_rot = 0

        self._x_cal = 0
        self._y_cal = 0
        self._z_cal = 0

        self._i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
        self._i2c.writeto_mem(0x68, 0x6B, bytes(1))  # Set SLEEP reg to 1
        self._i2c.writeto_mem(
            0x68, 0x1B, bytes(GYRO_RANGE_BYTES[self._gyro_range])
        )  # Set Gyro range

        self._is_running = False

        self._timer = Timer(-1)

    def _timer_callback(self, t: Timer):
        x, y, z = self.get_gyro_xyz()
        self._x_rot += x * self._timer_period
        self._y_rot += y * self._timer_period
        self._z_rot += z * self._timer_period

    def start(self):
        self._timer.init(
            period=int(self._timer_period * 1000), callback=self._timer_callback
        )
        self._is_running = True

    def stop(self):
        self._timer.deinit()
        self._is_running = False

    def get_gyro_xyz(self):
        # Inverted values because upside down gyro
        raw_data = self._i2c.readfrom_mem(0x68, 0x43, 6)
        x = -bytes_to_int(raw_data[0], raw_data[1]) / self._gyro_scale - self._x_cal
        y = -bytes_to_int(raw_data[2], raw_data[3]) / self._gyro_scale - self._y_cal
        z = -bytes_to_int(raw_data[4], raw_data[5]) / self._gyro_scale - self._z_cal
        return x, y, z

    def calibrate_offsets(self, iterations=10000):
        x_sum = 0
        y_sum = 0
        z_sum = 0
        for _ in range(iterations):
            x, y, z = self.get_gyro_xyz()
            x_sum += x
            y_sum += y
            z_sum += z

        self._x_cal = x_sum / iterations
        self._y_cal = y_sum / iterations
        self._z_cal = z_sum / iterations

    def automatic_calibration(self, robi, robi_config, turn_degree: float = 360):
        """
        Performs a 180° turn
        """

        assert self._is_running, "Gyro not running"

        motor_velocity = 0.03

        ir_distance = robi_config.track_width * pi * turn_degree / 360
        turn_time = ir_distance / motor_velocity

        robi.motors.left.set_direction(robi.motors.DIR_BACKWARD)
        robi.motors.right.set_direction(robi.motors.DIR_FORWARD)
        robi.motors.set_velocity(motor_velocity)

        start_degree = self.z_rot

        robi.motors.enable()
        time.sleep(turn_time)
        robi.motors.disable()

        end_degree = self.z_rot

        print(end_degree - start_degree)

    def interactive_calibration(self, turn_degree: float = 360):
        assert self._is_running, "Gyro not running"

        start_degree = self.z_rot
        print(f"Turn robi {turn_degree} degree")
        input("Press Enter to continue ")
        end_degree = self.z_rot
        measured_degree = abs(end_degree - start_degree)
        print(f"Measured {measured_degree} degree -> {abs(1 - measured_degree / turn_degree) * 100}% error.")

    @property
    def xyz_rot(self):
        return self._x_rot, self._y_rot, self._z_rot

    @property
    def x_rot(self):
        return self._x_rot

    @property
    def y_rot(self):
        return self._y_rot

    @property
    def z_rot(self):
        return self._z_rot


def main():
    gyro = Gyro()
    gyro.calibrate_offsets()
    print("Calibration complete")
    gyro.start()
    for i in range(100):
        print(gyro.xyz_rot)
        time.sleep(0.1)
    gyro.stop()


if __name__ == "__main__":
    main()
