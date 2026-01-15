import machine

from Robi42Lib.device_drivers.impl import vl53l0x, vl53l1x, base_driver

class VL53LXX(base_driver.I2C_BaseDriver):

    SUPPORTED_ADDRESSES = vl53l0x.VL53L0X.SUPPORTED_ADDRESSES | vl53l1x.VL53L1X.SUPPORTED_ADDRESSES

    def __init__(self, i2c: machine.I2C, address: int):
        super().__init__(i2c, address)
        try:
            self._impl = vl53l0x.VL53L0X(i2c, address)
        except vl53l0x.TimeoutError:
            self._impl = vl53l1x.VL53L1X(i2c, address)

    def measure_distance(self) -> int:
        distance: int
        if isinstance(self._impl, vl53l0x.VL53L0X):
            distance = abs(self._impl.ping() - 60)   # 60 = random gemessen mit der Hand davor gehalten
        elif isinstance(self._impl, vl53l1x.VL53L1X):
            distance = self._impl.read()
        else:
            raise NotImplemented()

        return distance
