# How to use custom char: https://microcontrollerslab.com/i2c-lcd-raspberry-pi-pico-micropython-tutorial/

from Robi42Lib.lib.machine_i2c_lcd import I2cLcd
from Robi42Lib.i2c_connections import laser_and_conns_i2c


class LCD(I2cLcd):
    def __init__(self):
        super().__init__(laser_and_conns_i2c, 0x3F, 2, 16)
        self.off()

    def off(self):
        self.clear()
        self.backlight_off()
        self.display_off()
        
    def on(self):
        self.backlight_on()
        self.display_on()
