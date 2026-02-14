# How to use custom char: https://microcontrollerslab.com/i2c-lcd-raspberry-pi-pico-micropython-tutorial/

from time import sleep

from . import base_module


class LCD(base_module.BaseModule):

    def __init__(self):
        ...

    def begin(self):
        self.turn_off()

    @base_module.get_first_i2c_hardware('HD44780_I2C_driver')
    def configure_cursor(
        self,
        show_cursor,
        blink_cursor,
        HD44780_I2C_driver=None
    ):
        if show_cursor:
            HD44780_I2C_driver.show_cursor()
        else:
            HD44780_I2C_driver.hide_cursor()

        if blink_cursor:
            HD44780_I2C_driver.blink_cursor_on()
        else:
            HD44780_I2C_driver.blink_cursor_off()

    @base_module.get_first_i2c_hardware('HD44780_I2C_driver')
    def set_cursor(self, x_pos: int, y_pos: int , HD44780_I2C_driver=None):
        HD44780_I2C_driver.move_to(x_pos, y_pos)

    @base_module.get_first_i2c_hardware('HD44780_I2C_driver')
    def turn_off(self, HD44780_I2C_driver=None):
        HD44780_I2C_driver.clear()
        HD44780_I2C_driver.backlight_off()
        HD44780_I2C_driver.display_off()

    @base_module.get_first_i2c_hardware('HD44780_I2C_driver')
    def turn_on(self, HD44780_I2C_driver=None):
        HD44780_I2C_driver.backlight_on()
        HD44780_I2C_driver.display_on()

    @base_module.get_first_i2c_hardware('HD44780_I2C_driver')
    def put_str(self, text: str, HD44780_I2C_driver=None):
        HD44780_I2C_driver.putstr(text)
