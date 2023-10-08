from time import sleep_ms

from . import base_module
from ..device_drivers.impl import vl53l0x as vl53l0x_driver


class LaserSensor(base_module.BaseModule):

    @base_module.get_first_i2c_hardware('VL53L0X')
    def read_distance_mm(self, VL53L0X: vl53l0x_driver.VL53L0X | None=None):
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.

        60 = random gemessen mit der Hand davor gehalten
        """
        sleep_ms(20)
        distance: int = VL53L0X.ping()
        return abs(distance - 60)
