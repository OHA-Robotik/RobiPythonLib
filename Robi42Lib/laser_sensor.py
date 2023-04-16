from machine import I2C, Pin
from Robi42Lib.lib.vl53l0x import VL53L0X
from time import sleep_ms
from Robi42Lib.i2c_connections import laser_and_conns_i2c


class LaserSensor:
    def __init__(self) -> None:
        self.__vl53l0x = VL53L0X(laser_and_conns_i2c)

    def get_distance(self):
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.
        """
        sleep_ms(20)
        return self.__vl53l0x.ping() - 60
