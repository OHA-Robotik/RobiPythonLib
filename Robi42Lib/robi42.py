from .modules import buttons as _mod_buttons
from .modules import gyro as _mod_gyro
from .modules import ir_sensor as _mod_ir_sensor
from .modules import laser_sensor as _mod_laser_sensor
from .modules import lcd as _mod_lcd
from .modules import led as _mod_led
from .modules import motor as _mod_motor
from .modules import piezo as _mod_piezo
from .modules import poti as _mod_poti
from .modules import eeprom as _mod_eeprom
from .modules import base_module as _base_mod

class Robi42:
    """
    Robi42 is the main class that provides access to all hardware components
    such as motors, buttons, piezo, LEDs, and sensors.
    """

    def __init__(self):
        """
        Initializes all the hardware modules of Robi42.
        """
        self.motors = _mod_motor.Motors()
        self.buttons = _mod_buttons.Buttons()
        self.piezo = _mod_piezo.Piezo()
        self.poti = _mod_poti.Poti()
        self.leds = _mod_led.Leds()
        self.ir_sensors = _mod_ir_sensor.IrSensors()
        self.lcd = _mod_lcd.LCD()
        self.laser_sensor = _mod_laser_sensor.LaserSensor()
        self.gyro = _mod_gyro.Gyro()
        self.external_storage = _mod_eeprom.ExternalStorage()

        self._modules: list[_base_mod.BaseModule] = [
            self.motors,
            self.buttons,
            self.piezo,
            self.poti,
            self.leds,
            self.ir_sensors,
            self.lcd,
            self.laser_sensor,
            self.gyro,
            self.external_storage
        ]

    def begin(self):
        for mod in self._modules:
            mod.begin()
