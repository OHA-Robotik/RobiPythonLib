from time import sleep_ms

from . import base_module


class LaserSensor(base_module.BaseModule):

    @base_module.need_i2c_hardware('vl53l0x')
    def read_distance_mm(self, vl53l0x=None):
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.

        60 = random gemessen mit der Hand davor gehalten
        """
        sleep_ms(20)
        return abs(vl53l0x.ping() - 60)
