import time
import _thread
from machine import Timer

from . import platform_description
from ..device_drivers import inventory as driver_inventory


class HardwareManager():
    __INSTANCE = None
    __INIT_TOKEN = object()

    @classmethod
    def get_instance(cls) -> 'HardwareManager':
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls(cls.__INIT_TOKEN)
        return cls.__INSTANCE

    def __init__(self, init_token: object) -> None:
        if init_token != self.__INIT_TOKEN:
            raise RuntimeError('Cannot explicitly instanciate singleton class. ')
        self.platform_loader = platform_description.PlatformLoader.get_instance()
        self.loaded_i2c_drivers = {i: {} for i in range(len(self.platform_loader.get_platform().get('i2c', [])))}

        self.i2c_rediscovery_timer = Timer()
        self.i2c_rediscovery_timer.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:self.discover_hardware())

    def discover_hardware(self):
        self.discover_i2c_hardware()

    def discover_i2c_hardware(self):
        for i2c_num, i2c_phy in enumerate(self.platform_loader.get_platform().get('i2c', [])):
            currently_loaded_drivers = self.loaded_i2c_drivers[i2c_num]
            devices = i2c_phy.scan()
            for address in devices:
                if address in currently_loaded_drivers:
                    # hardware is already initalized, nothing to do here
                    continue
                # look for a matching driver
                selected_driver = None
                for driver in driver_inventory.I2C_DRIVERS:
                    if address in driver.SUPPORTED_ADDRESSES:
                        selected_driver = driver
                        break
                if selected_driver is not None:
                    print('Instanciate', selected_driver.__name__)
                    currently_loaded_drivers[address] = selected_driver(i2c_phy, address)
            # destruct drivers of hardware that has been removed
            addresses_to_destruct = set(currently_loaded_drivers.keys()) - set(devices)
            for address in addresses_to_destruct:
                print('Destroying driver:', currently_loaded_drivers[address].__class__.__name__)
                del currently_loaded_drivers[address]
