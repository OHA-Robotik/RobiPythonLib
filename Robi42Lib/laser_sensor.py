from time import sleep_ms

from Robi42Lib.i2c_connections import laser_and_conns_i2c
from Robi42Lib.lib.vl53l0x import VL53L0X


class LaserSensor:
    def __init__(self) -> None:
        self.__vl53l0x = VL53L0X(laser_and_conns_i2c)

    def read_distance_mm(self):
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.

        60 = random gemessen mit der Hand davor gehalten
        """
        sleep_ms(20)
        return abs(self.__vl53l0x.ping() - 60)
