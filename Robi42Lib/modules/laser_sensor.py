from time import sleep_ms

from . import base_module


class LaserSensor(base_module.BaseModule):
    def __init__(self) -> None:
        self.__vl53l0x = base_module.BoardDevices('laser')

    def read_distance_mm(self):
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.

        60 = random gemessen mit der Hand davor gehalten
        """
        sleep_ms(20)
        return abs(self.__vl53l0x.ping() - 60)
