from . import base_module

import utime


class Gyro(base_module.BaseModule):

    __last_pitch = 0
    __last_roll = 0
    __prev_time = utime.ticks_ms()

    @base_module.need_i2c_hardware('mpu6050')
    def get_temperature(self, mpu6050=None) -> float:
        """
        Returns the temperature in °C
        """
        return mpu6050.get_temperature()

    @base_module.need_i2c_hardware('mpu6050')
    def get_acceleration(self, mpu6050=None) -> tuple[float, float, float]:
        """
        Returns the acceleration in g
        """
        return mpu6050.get_acceleration()

    @base_module.need_i2c_hardware('mpu6050')
    def get_gyro(self, mpu6050=None) -> tuple[float, float, float]:
        """
        Returns the gyroscope in °/s
        """
        return mpu6050.get_gyro()

    @base_module.need_i2c_hardware('mpu6050')
    def get_all_data(
        self,
        mpu6050=None,
    ) -> dict[
        str:float,
        str : dict[str:float, str:float, str:float],
        str : dict[str:float, str:float, str:float],
    ]:
        return mpu6050.get_data()

    @base_module.need_i2c_hardware('mpu6050')
    def get_tilt_angles(self, mpu6050=None) -> tuple[float, float, float]:
        """
        Calculates the rotation in degree
        """
        return mpu6050.calculate_tilt_angles(*self.get_acceleration())

    @base_module.need_i2c_hardware('mpu6050')
    def get_pitch_and_roll(self, mpu6050=None) -> tuple[float, float]:
        curr_time = utime.ticks_ms()
        dt = (curr_time - self.__prev_time) / 1000
        gyro = self.get_gyro()
        pitch = mpu6050.get_pitch(self.__last_pitch, gyro, dt)
        roll = mpu6050.get_roll(self.__last_roll, gyro, dt)
        self.__prev_time = curr_time
        return pitch, roll

    def _calibrate(self):
        raise NotImplementedError()
