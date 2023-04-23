from Robi42Lib.gyro import *
from Robi42Lib.piezo import *
from Robi42Lib.lcd import *
from Robi42Lib.led import Leds
from Robi42Lib.motor import Motors
from Robi42Lib.buttons import Buttons
from Robi42Lib.laser_sensor import LaserSensor
from Robi42Lib.poti import Poti
from Robi42Lib.ir_sensor import IrSensors
from time import sleep


class Robi42:
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
        enable_ir_sensors=True
    ):
        self.enable_lcd = enable_lcd
        self.enable_piezo = enable_piezo
        self.enable_leds = enable_leds
        self.enable_motors = enable_motors

        if enable_gyro:
            self.gyro = Gyro()
        if enable_piezo:
            self.piezo = Piezo()
        if enable_lcd:
            self.lcd = LCD()
        if enable_leds:
            self.leds = Leds()
        if enable_motors:
            self.motors = Motors()
        if enable_buttons:
            self.buttons = Buttons()
        if enable_laser_sensor:
            self.laser_sensor = LaserSensor()
        if enable_poti:
            self.poti = Poti()
        if enable_ir_sensors:
            self.ir_sensors = IrSensors()

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type, exc_val, exc_tb):
        self.stop(exc_type, exc_val, exc_tb)

    def __del__(self):
        self.stop()

    def stop(self, exc_type: type = None, exc_val=None, exc_tb=None):
        self._display_exception(exc_type, exc_val, exc_tb)

        if self.enable_piezo:
            self.piezo._turn_off()
        if self.enable_lcd:
            self.lcd.off()
        if self.enable_leds:
            self.leds.off()
        if self.enable_motors:
            self.motors.disable()

    def _display_exception(self, exc_type: type, exc_val, exc_tb):
        if exc_type is not None:
            print("!--Exception--!")
            print(exc_type.__name__)

            if str(exc_val) != "":
                print(exc_val)

            if exc_tb is not None:
                print(exc_tb)

            while self.enable_lcd:
                self.lcd.on()

                self.lcd.clear()
                self.lcd.putstr("!--Exception--!")
                sleep(1)

                self.lcd.clear()
                self.lcd.put_large_str(exc_type.__name__, 3)
                sleep(1)

                if str(exc_val) != "":
                    self.lcd.clear()
                    self.lcd.putstr("Execption value:")

                    sleep(1)
                    self.lcd.clear()
                    self.lcd.put_large_str(str(exc_val), 3)

        else:
            print("Robi finished executing")
