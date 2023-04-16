from Robi42Lib.gyro import *
from Robi42Lib.piezo import *
from Robi42Lib.lcd import *
from Robi42Lib.led import Leds
from Robi42Lib.motor import Motors
from Robi42Lib.buttons import Buttons
from Robi42Lib.laser_sensor import LaserSensor
from Robi42Lib.poti import Poti
from time import sleep


class Robi42:
    def __init__(self):
        self.gyro = Gyro()
        self.piezo = Piezo()
        self.lcd = LCD()
        self.leds = Leds()
        self.motors = Motors()
        self.buttons = Buttons()
        self.laser_sensor = LaserSensor()
        self.poti = Poti()

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type, exc_val, exc_tb):

        if exc_type is not None:

            print("!--Exeption--!")
            print(exc_type.__name__)

            if str(exc_val) != "":
                print(exc_val)

            if exc_tb is not None:
                print(exc_tb)

            while True:

                self.lcd.on()

                self.lcd.clear()
                self.lcd.putstr("!--Exeption--!")
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

        self.piezo._turn_off()
        self.lcd.off()
        self.leds.off()
        self.motors.disable()
