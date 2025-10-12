from time import sleep_ms

from . import base_module
from ..device_drivers.impl import vl53l0x as vl53l0x_driver
from ..device_drivers.impl import vl53l1x as vl53l1x_driver

class LaserSensor(base_module.BaseModule):

    @base_module.get_first_i2c_hardware_any(vl53l0x_driver.VL53L0X, vl53l1x_driver.VL53L1X)
    def read_distance_mm(self, device=None):
        sleep_ms(20)
        if isinstance(device, vl53l0x_driver.VL53L0X):
            distance = abs(device.ping() - 60)
        elif isinstance(device, vl53l1x_driver.VL53L1X):
            distance = device.read()
        else:
            raise TypeError("Unsupported device type.")
        
        return distance
    