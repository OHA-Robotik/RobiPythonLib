import machine
from ..device_drivers.impl import mcp3008 as drv_mcp3008  # analog device driver
from ..device_drivers.impl import mcp23S17 as drv_mcp23s17  # digital device driver


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
            raise RuntimeError('Cannot explicitly instantiate singleton class. ')
        self.__init_platform()
        self.__init_board_pins()
        self.__driver_preferences = {
            'hd44780_i2c': {
                'num_lines': 2,
                'num_columns': 16
            },
        }

    def __init_board_pins(self):
        # init board pin by getting a SPIHardwareHolder object. This asserts that the singleton
        # has been instanciated
        SPIHardwareHolder.get_instance()

    def __init_platform(self):
        self.__platform = {
            'i2c': [
                # no hardware-bus-mapping needed. We will discover the hw by a scan and don't
                # really care where it is plugged into. 
                machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17), freq=400000),
                machine.I2C(1, sda=machine.Pin(18), scl=machine.Pin(19), freq=400000),
            ],
        }

    def get_platform(self) -> dict:
        return self.__platform

    def get_preference_for_driver(self, driver_name: str) -> dict:
        if driver_name not in self.__driver_preferences:
            raise ValueError('Cannot find driver preferences for \'{}\''.format(driver_name))
        return self.__driver_preferences[driver_name]


class SPIHardwareHolder():
    __INSTANCE = None
    __INIT_TOKEN = object()

    @classmethod
    def get_instance(cls) -> 'SPIHardwareHolder':
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls(cls.__INIT_TOKEN)
        return cls.__INSTANCE

    def __init__(self, init_token: object) -> None:
        if init_token != self.__INIT_TOKEN:
            raise RuntimeError('Cannot explicitly instanciate singleton class. ')
        
        self.__init_spi()
        self.__init_digital()
        self.__init_analog()

    def __init_spi(self) -> None:
        self.spi_analog = machine.SPI(
            0,
            baudrate=1000000,
            polarity=1,
            phase=1,
            bits=8,
            firstbit=machine.SPI.MSB,
            sck=machine.Pin(2),
            mosi=machine.Pin(3),
            miso=machine.Pin(4),
        )
        self.spi_analog_cs = machine.Pin(5, machine.Pin.OUT)

        self.spi_digital = machine.SPI(
            1,
            baudrate=1000000,
            polarity=1,
            phase=1,
            bits=8,
            firstbit=machine.SPI.MSB,
            sck=machine.Pin(10),
            mosi=machine.Pin(11),
            miso=machine.Pin(12),
        )
        self.spi_digital_cs = machine.Pin(13, machine.Pin.OUT)

    def __init_digital(self):
        self.mcp_motor_taster = drv_mcp23s17.MCP23S17(self.spi_digital, self.spi_digital_cs, 0)
        self.mcp_motor_taster.open()
        self.mcp_leds = drv_mcp23s17.MCP23S17(self.spi_digital, self.spi_digital_cs, 1)
        self.mcp_leds.open()
        self.mcp23s17_by_index = [self.mcp_motor_taster, self.mcp_leds]

    def __init_analog(self):
        self.mcp_analog = drv_mcp3008.MCP3008(self.spi_analog, self.spi_analog_cs)


class BoardPins():
    btn_up = 'btn_up'
    btn_down = 'btn_down'
    btn_center = 'btn_center'
    btn_left = 'btn_left'
    btn_right = 'btn_right'
    mr_en = 'mr_en'
    mr_dir = 'mr_dir'
    mr_m0 = 'mr_m0'
    mr_m1 = 'mr_m1'
    mr_m2 = 'mr_m2'
    ml_en = 'ml_en'
    ml_dir = 'ml_dir'
    ml_m0 = 'ml_m0'
    ml_m1 = 'ml_m1'
    ml_m2 = 'ml_m2'
    led_sl = 'led_sl'
    led_sr = 'led_sr'
    led_bl_lv = 'led_bl_lv'
    led_bl_rv = 'led_bl_rv'
    led_bl_lh = 'led_bl_lh'
    led_bl_rh = 'led_bl_rh'
    led_rl = 'led_rl'
    led_rr = 'led_rr'


class DigitalBoardPin():
    PIN_LOOKUP = {
        # chip 0
        BoardPins.btn_up: (0, 11),
        BoardPins.btn_down: (0, 12),
        BoardPins.btn_center: (0, 8),
        BoardPins.btn_left: (0, 9),
        BoardPins.btn_right: (0, 10),

        BoardPins.mr_en: (0, 14),
        BoardPins.mr_dir: (0, 3),
        BoardPins.mr_m0: (0, 0),
        BoardPins.mr_m1: (0, 1),
        BoardPins.mr_m2: (0, 2),

        BoardPins.ml_en: (0, 15),
        BoardPins.ml_dir: (0, 7),
        BoardPins.ml_m0: (0, 4),
        BoardPins.ml_m1: (0, 5),
        BoardPins.ml_m2: (0, 6),

        # chip 1
        BoardPins.led_sl: (1, 0),
        BoardPins.led_sr: (1, 1),
        BoardPins.led_bl_lv: (1, 2),
        BoardPins.led_bl_rv: (1, 3),
        BoardPins.led_bl_lh: (1, 4),
        BoardPins.led_bl_rh: (1, 5),
        BoardPins.led_rl: (1, 6),
        BoardPins.led_rr: (1, 7),
        # expansion ports still unmapped
    }

    OUT = 0
    IN = 1

    PULL_UP = True
    PULL_NONE = False

    # TODO: Actually implement the enum. Right now it is just a shortcut for the right string.
    def __init__(self, pin_id: str, mode=OUT, pull=PULL_NONE) -> None:
        if pin_id not in self.PIN_LOOKUP:
            raise ValueError('Cannot find pin \'{}\'!'.format(pin_id))
        
        mcp_index, self.__mcp_pin_num = self.PIN_LOOKUP[pin_id]
        # get the right mcp object
        self.__mcp_obj = SPIHardwareHolder.get_instance().mcp23s17_by_index[mcp_index]
        self.__mcp_obj.set_direction(
            self.__mcp_pin_num,
            drv_mcp23s17.MCP23S17.DIR_OUTPUT if mode == 0 else drv_mcp23s17.MCP23S17.DIR_INPUT
        )
        self.__mcp_obj.set_pullup(self.__mcp_pin_num, pull)
    
    def value(self, level = None):
        if level is None:
            return self.__mcp_obj.digital_read(self.__mcp_pin_num)
        else:
            self.__mcp_obj.digital_write(self.__mcp_pin_num, level)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)
