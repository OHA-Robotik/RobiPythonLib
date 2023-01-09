from Robi42Lib.gyro import *
from Robi42Lib.piezo import *
from Robi42Lib.lcd import *
from Robi42Lib.led import Led, Leds
from Robi42Lib.motor import MotorLeft, MotorRight

class Robi42:

    gyro: Gyro
    piezo: Piezo
    lcd: LCD
    leds: Leds
    motor_left: MotorLeft
    motor_right: MotorRight

    def __init__(self):
        self.gyro = Gyro()
        self.piezo = Piezo()
        self.lcd = LCD()
        self.leds = Leds()
        self.motor_left = MotorLeft()
        self.motor_right = MotorRight()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.piezo._turn_off()
        self.lcd.off()
        self.leds.all_off()
        self.motor_left.disable()
        self.motor_right.disable()
