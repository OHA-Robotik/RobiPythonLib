# How to use custom char: https://microcontrollerslab.com/i2c-lcd-raspberry-pi-pico-micropython-tutorial/

from time import sleep

from . import base_module


class LCD(base_module.BaseModule):

    @base_module.need_i2c_hardware('hd44780_i2c')
    def turn_off(self, hd44780_i2c=None):
        hd44780_i2c.clear()
        hd44780_i2c.backlight_off()
        hd44780_i2c.display_off()

    @base_module.need_i2c_hardware('hd44780_i2c')
    def turn_on(self, hd44780_i2c=None):
        hd44780_i2c.backlight_on()
        hd44780_i2c.display_on()

    @base_module.need_i2c_hardware('hd44780_i2c')
    def put_large_str(self, s: str, delay: int = 1, hd44780_i2c=None):
        for i in range(0, len(s), 32):
            self.clear()
            if i + 32 < len(s):
                hd44780_i2c.putstr(s[i: i + 32])
            else:
                hd44780_i2c.putstr(s[i:])
            sleep(delay)
