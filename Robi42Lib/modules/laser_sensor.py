from time import sleep_ms

from . import base_module
from ..device_drivers.impl import vl53lxx as vl53lxx_driver


class LaserSensor(base_module.BaseModule):

    @base_module.get_first_i2c_hardware('VL53LXX')
    def read_distance_mm(self, VL53LXX: vl53lxx_driver.VL53LXX | None=None) -> int:
        """
        Returns the distance in mm.
        Takes 20ms for cooldown.
        """
        sleep_ms(20)
        return VL53LXX.measure_distance()
