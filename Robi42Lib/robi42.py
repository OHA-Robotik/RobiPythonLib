from .modules import buttons as _mod_buttons
from .modules import piezo as _mod_piezo
from .modules import motor as _mod_motor
from .modules import poti as _mod_poti
from .modules import led as _mod_led
from .modules import ir_sensor as _mod_ir_sensor
from .modules import lcd as _mod_lcd
from .modules import gyro as _mod_gyro
from .modules import laser_sensor as _mod_laser_sensor

from .rsrc.impl.rsrc_frame import RSRCFrame as _RSRCFrame


class Robi42:

    def __init__(
        self,
    ):
        self.motors = _mod_motor.Motors()
        self.buttons = _mod_buttons.Buttons()
        self.piezo = _mod_piezo.Piezo()
        self.poti = _mod_poti.Poti()
        self.leds = _mod_led.Leds()
        self.ir_sensors = _mod_ir_sensor.IrSensors()
        self.lcd = _mod_lcd.LCD()
        self.laser_sensor = _mod_laser_sensor.LaserSensor()
        self.gyro = _mod_gyro.Gyro()

    def sample_state(self, frame_id: int) -> _RSRCFrame:
        return _RSRCFrame.sample(self, frame_id)
