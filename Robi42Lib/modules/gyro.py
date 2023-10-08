from . import base_module

import utime


class Gyro(base_module.BaseModule):

    __last_pitch = 0
    __last_roll = 0
    __prev_time = utime.ticks_ms()

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_temperature(self, MPU6050=None) -> float:
        """
        Returns the temperature in °C
        """
        return MPU6050.temperature

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_acceleration(self, MPU6050=None) -> tuple[float, float, float]:
        """
        Returns the acceleration in g
        """
        return MPU6050.get_acceleration()

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_gyro(self, MPU6050=None) -> tuple[float, float, float]:
        """
        Returns the gyroscope in °/s
        """
        return MPU6050.get_gyro()

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_all_data(
        self,
        MPU6050=None,
    ) -> dict[
        str:float,
        str : dict[str:float, str:float, str:float],
        str : dict[str:float, str:float, str:float],
    ]:
        return MPU6050.get_data()

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_tilt_angles(self, MPU6050=None) -> tuple[float, float, float]:
        """
        Calculates the rotation in degree
        """
        return MPU6050.calculate_tilt_angles(*self.get_acceleration())

    @base_module.get_first_i2c_hardware('MPU6050')
    def get_pitch_and_roll(self, MPU6050=None) -> tuple[float, float]:
        curr_time = utime.ticks_ms()
        dt = (curr_time - self.__prev_time) / 1000
        gyro = self.get_gyro()
        pitch = MPU6050.get_pitch(self.__last_pitch, gyro, dt)
        roll = MPU6050.get_roll(self.__last_roll, gyro, dt)
        self.__prev_time = curr_time
        return pitch, roll

    def _calibrate(self):
        raise NotImplementedError()
