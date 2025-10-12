import time
import _thread
from machine import Timer

from . import platform_description
from ..device_drivers import inventory as driver_inventory
from ..device_drivers.impl import vl53l0x


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
            raise RuntimeError('Cannot explicitly instantiate singleton class. ')
        self.platform_loader = platform_description.PlatformLoader.get_instance()
        self.i2c_drivers_by_address = {i: {} for i in range(len(self.platform_loader.get_platform().get('i2c', [])))}
        self.i2c_drivers_by_name = {}
        self.discover_i2c_hardware()

        # start timer
        self.i2c_rediscovery_timer = Timer()
        self.i2c_rediscovery_timer.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:self.discover_i2c_hardware())

    def get_i2c_driver_by_name(self, name: str) -> list:
        return self.i2c_drivers_by_name.get(name, [])

    def discover_i2c_hardware(self) -> None:
        for i2c_num, i2c_phy in enumerate(self.platform_loader.get_platform().get('i2c', [])):
            currently_loaded_drivers = self.i2c_drivers_by_address[i2c_num]
            devices = i2c_phy.scan()
            for address in devices:
                if address in currently_loaded_drivers:
                    # hardware is already initialized, nothing to do here
                    continue
                # look for a matching driver
                for driver in driver_inventory.I2C_DRIVERS:
                    if address in driver.SUPPORTED_ADDRESSES:
                        selected_driver = driver

                        print('Instantiating', selected_driver.__name__ + '... ', end='')

                        try:
                            driver_obj = selected_driver(i2c_phy, address)
                        except vl53l0x.TimeoutError:
                            print('Failed')
                            continue

                        currently_loaded_drivers[address] = driver_obj

                        if selected_driver.__name__ not in self.i2c_drivers_by_name:
                            self.i2c_drivers_by_name[selected_driver.__name__] = []

                        self.i2c_drivers_by_name[selected_driver.__name__].append(driver_obj)

                        print('Success')

                        break

            # destruct drivers of hardware that has been removed
            addresses_to_destruct = set(currently_loaded_drivers.keys()) - set(devices)
            for address in addresses_to_destruct:
                driver_class_name = currently_loaded_drivers[address].__class__.__name__
                print('Destroying driver:', driver_class_name)
                driver_obj = currently_loaded_drivers[address]
                self.i2c_drivers_by_name[driver_class_name].remove(driver_obj)
                del currently_loaded_drivers[address]
