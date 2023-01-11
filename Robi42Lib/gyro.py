from Robi42Lib.lib.imu import MPU6050
from time import sleep_ms
from Robi42Lib.i2c_connections import gyro_and_led_i2c


class Gyro:
    def __init__(self):
        self.__mpu = MPU6050(gyro_and_led_i2c)

    def get_gyro_xyz(self):
        """
        Returns the rotation around the X, Y and Z axis.
        It takes 10ms for cooldown
        """
        sleep_ms(10)
        return self._get_gyro_xyz_no_wait()

    def _get_gyro_xyz_no_wait(self):
        return self.__mpu.gyro.x, self.__mpu.gyro.y, self.__mpu.gyro.z

    def get_acceleration_xyz(self):
        """
        Returns the acceleration of the X, Y and Z axis.
        It takes 10ms for cooldown
        """
        sleep_ms(10)
        return self._get_accerleration_xyz_no_wait()

    def _get_accerleration_xyz_no_wait(self):
        return self.__mpu.accel.x, self.__mpu.accel.y, self.__mpu.accel.z

    def get_temperature(self):
        """
        It takes 10ms for cooldown
        """
        sleep_ms(10)
        return self._get_temperature_no_wait()

    def _get_temperature_no_wait(self):
        return self.__mpu.temperature

    def _calibrate(self):
        raise NotImplementedError()
