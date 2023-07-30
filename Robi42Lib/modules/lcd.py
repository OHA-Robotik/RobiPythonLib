# How to use custom char: https://microcontrollerslab.com/i2c-lcd-raspberry-pi-pico-micropython-tutorial/

from time import sleep

from . import base_module


class LCD(base_module.BaseModule):
    def __init__(self):
        self.lcd = base_module.BoardDevices('lcd')

    def turn_off(self):
        self.lcd.clear()
        self.lcd.backlight_off()
        self.lcd.display_off()

    def turn_on(self):
        self.lcd.backlight_on()
        self.lcd.display_on()

    def put_large_str(self, s: str, delay: int = 1):
        for i in range(0, len(s), 32):
            self.clear()
            if i + 32 < len(s):
                self.lcd.putstr(s[i: i + 32])
            else:
                self.lcd.putstr(s[i:])
            sleep(delay)
