from . import base_module


class PowerMeter(base_module.BaseModule):

    @base_module.need_i2c_hardware('ina226')
    def read_values(self, ina226=None):
        return {
            'power': ina226.power,
            'current': ina226.current,
            'bus_voltage': ina226.bus_voltage,
            'shunt_voltage': ina226.shunt_voltage,
        }


# import ina226
# from time import sleep
# from machine import Pin, I2C
# # i2c
# i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)
# # ina226
# ina = ina226.INA226(i2c, 0x40)
# # default configuration and calibration value
# ina.set_calibration()
# print(ina.power)
# print(ina.current)
# print(ina.bus_voltage)
# print(ina.shunt_voltage)
