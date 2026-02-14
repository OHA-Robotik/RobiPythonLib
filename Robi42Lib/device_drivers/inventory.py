# i2c
from .impl import hd44780_i2c, vl53l0x, mpu6050, vl53l1x, eeprom_i2c
# spi
from .impl import mcp3008, mcp23S17

I2C_DRIVERS = [
    hd44780_i2c.HD44780_I2C_driver,
    vl53l0x.VL53L0X,
    mpu6050.MPU6050,
    vl53l1x.VL53L1X,
    eeprom_i2c.EEPROM_24LC256_I2C_driver
]

SPI_DRIVERS = {
    'mcp3008': mcp3008.MCP3008,
    'mcp23s17': mcp23S17.MCP23S17,
}
