from time import sleep

from Robi42Lib.buttons import Buttons
from Robi42Lib.gyro import *
from Robi42Lib.ir_sensor import IrSensors
from Robi42Lib.laser_sensor import LaserSensor
from Robi42Lib.lcd import *
from Robi42Lib.led import Leds
from Robi42Lib.motor import Motors
from Robi42Lib.piezo import *
from Robi42Lib.poti import Poti
from Robi42Lib.voltage_reader import VoltageReader


class Robi42:

    enable_lcd = False
    enable_piezo = False
    enable_leds = False
    enable_motors = False

    def __init__(
        self,
        *,
        enable_gyro=True,
        enable_piezo=True,
        enable_lcd=True,
        enable_leds=True,
        enable_motors=True,
        enable_buttons=True,
        enable_laser_sensor=True,
        enable_poti=True,
        enable_ir_sensors=True,
        enable_voltage_reader=True,
    ):

        if enable_gyro:
            self.init_gyro()
        if enable_piezo:
            self.init_piezo()
        if enable_lcd:
            self.init_lcd()
        if enable_leds:
            self.init_leds()
        if enable_motors:
            self.init_motors()
        if enable_buttons:
            self.init_buttons()
        if enable_laser_sensor:
            self.init_laser_sensor()
        if enable_poti:
            self.init_poti()
        if enable_ir_sensors:
            self.init_ir_sensors()
        if enable_voltage_reader:
            self.init_voltage_reader()

    def init_gyro(self):
        self.gyro = Gyro()

    def init_piezo(self):
        self.piezo = Piezo()
        self.enable_piezo = True

    def init_lcd(self):
        self.lcd = LCD()
        self.enable_lcd = True

    def init_leds(self):
        self.leds = Leds()
        self.enable_leds = True

    def init_motors(self):
        self.motors = Motors()
        self.enable_motors = True

    def init_buttons(self):
        self.buttons = Buttons()

    def init_laser_sensor(self):
        self.laser_sensor = LaserSensor()

    def init_poti(self):
        self.poti = Poti()

    def init_ir_sensors(self):
        self.ir_sensors = IrSensors()

    def init_voltage_reader(self):
        self.voltage_reader = VoltageReader()

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type, exc_val, exc_tb):
        self.stop(exc_type, exc_val, exc_tb)

    def __del__(self):
        self.stop()

    def stop(self, exc_type: type = None, exc_val=None, exc_tb=None):

        if self.enable_piezo:
            self.piezo.deinit()
        if self.enable_leds:
            self.leds.turn_all_off()
        if self.enable_motors:
            self.motors.disable()

        self._display_exception(exc_type, exc_val, exc_tb)

        if self.enable_lcd:
            self.lcd.turn_off()

    def _display_exception(self, exc_type: type, exc_val, exc_tb):
        if exc_type is not None:
            print("!---Exception--!")
            print(exc_type.__name__)

            if str(exc_val) != "":
                print(exc_val)

            if exc_tb is not None:
                print(exc_tb)

            while self.enable_lcd:
                self.lcd.turn_on()

                self.lcd.clear()
                self.lcd.putstr("!---Exception--!")
                sleep(1)

                self.lcd.clear()
                self.lcd.put_large_str(exc_type.__name__, 3)
                sleep(1)

                if str(exc_val) != "":
                    self.lcd.clear()
                    self.lcd.putstr("Exception value:")

                    sleep(1)
                    self.lcd.clear()
                    self.lcd.put_large_str(str(exc_val), 3)

        else:
            print("Robi finished executing")
