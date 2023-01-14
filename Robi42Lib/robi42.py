from Robi42Lib.gyro import *
from Robi42Lib.piezo import *
from Robi42Lib.lcd import *
from Robi42Lib.led import Leds
from Robi42Lib.motor import Motors
from Robi42Lib.buttons import Buttons


class Robi42:
    def __init__(self):
        self.gyro = Gyro()
        self.piezo = Piezo()
        self.lcd = LCD()
        self.leds = Leds()
        self.motors = Motors()
        self.buttons = Buttons()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.piezo._turn_off()
        self.lcd.off()
        self.leds.off()
        self.motors.disable()
