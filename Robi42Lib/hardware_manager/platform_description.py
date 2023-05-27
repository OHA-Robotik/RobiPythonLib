import machine


# ToDo: For future hardware revisions we need to determine which pinout to load here...
class PlatformLoader():
    __INSTANCE = None
    __INIT_TOKEN = object()

    @classmethod
    def get_instance(cls) -> 'PlatformLoader':
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls(cls.__INIT_TOKEN)
        return cls.__INSTANCE

    def __init__(self, init_token: object) -> None:
        if init_token != self.__INIT_TOKEN:
            raise RuntimeError('Cannot explicitly instanciate singleton class. ')
        self.__init_platform()
        self.__driver_preferences = {
            'hd44780_i2c': {
                'num_lines': 2,
                'num_columns': 16
            },
        }

    def __init_platform(self):
        self.__platform = {
            'i2c': [
                # no hardware-bus-mapping needed. We will discover the hw by a scan and don't
                # really care where it is plugged into. 
                machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17), freq=400000),
                machine.I2C(1, sda=machine.Pin(18), scl=machine.Pin(19), freq=400000),
            ],
            'spi': [
                # (spi_interface, select_pin, hw_usages),
                (
                    machine.SPI(
                        0,
                        baudrate=1000000,
                        polarity=1,
                        phase=1,
                        bits=8,
                        firstbit=machine.SPI.MSB,
                        sck=machine.Pin(2),
                        mosi=machine.Pin(3),
                        miso=machine.Pin(4),
                    ),
                    machine.Pin(5, machine.Pin.OUT),
                    {'leds', 'motor_taster', },
                ),
                (
                    machine.SPI(
                        1,
                        baudrate=1000000,
                        polarity=1,
                        phase=1,
                        bits=8,
                        firstbit=machine.SPI.MSB,
                        sck=machine.Pin(10),
                        mosi=machine.Pin(11),
                        miso=machine.Pin(12),
                    ),
                    machine.Pin(13, machine.Pin.OUT),
                    {'analog', },
                ),
            ],
        }

    def get_platform(self) -> dict:
        return self.__platform

    def get_preference_for_driver(self, driver_name: str) -> dict:
        if driver_name not in self.__driver_preferences:
            raise ValueError('Cannot find driver preferences for \'{}\''.format(driver_name))
        return self.__driver_preferences[driver_name]
