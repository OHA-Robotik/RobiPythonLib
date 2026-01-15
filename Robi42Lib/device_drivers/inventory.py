# i2c
from .impl import hd44780_i2c, vl53lxx, mpu6050
# spi
from .impl import mcp3008, mcp23S17

I2C_DRIVERS = [
    hd44780_i2c.HD44780_I2C_driver,
    vl53lxx.VL53LXX,
    mpu6050.MPU6050,
]

SPI_DRIVERS = {
    'mcp3008': mcp3008.MCP3008,
    'mcp23s17': mcp23S17.MCP23S17,
}
