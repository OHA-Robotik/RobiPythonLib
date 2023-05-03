from Robi42Lib.i2c_connections import gyro_and_led_i2c
from Robi42Lib.lib.mpu6050 import MPU6050
import utime


class Gyro:

    __last_pitch = 0
    __last_roll = 0
    __prev_time = utime.ticks_ms()

    def __init__(self):
        self.__mpu = MPU6050(gyro_and_led_i2c)

    def get_temperature(self) -> float:
        """
        Returns the temperature in °C
        """
        return self.__mpu.get_temperature()

    def get_acceleration(self) -> tuple[float, float, float]:
        """
        Returns the acceleration in g
        """
        return self.__mpu.get_acceleration()

    def get_gyro(self) -> tuple[float, float, float]:
        """
        Returns the gyroscope in °/s
        """
        return self.__mpu.get_gyro()

    def get_all_data(
        self,
    ) -> dict[
        str:float,
        str : dict[str:float, str:float, str:float],
        str : dict[str:float, str:float, str:float],
    ]:
        return self.__mpu.get_data()

    def get_tilt_angles(self) -> tuple[float, float, float]:
        """
        Calculates the rotation in degree
        """
        return self.__mpu.calculate_tilt_angles(*self.get_acceleration())

    def get_pitch_and_roll(self) -> tuple[float, float]:
        curr_time = utime.ticks_ms()
        dt = (curr_time - self.__prev_time) / 1000
        gyro = self.get_gyro()
        pitch = self.__mpu.get_pitch(self.__last_pitch, gyro, dt)
        roll = self.__mpu.get_roll(self.__last_roll, gyro, dt)
        self.__prev_time = curr_time
        return pitch, roll

    def _calibrate(self):
        raise NotImplementedError()
