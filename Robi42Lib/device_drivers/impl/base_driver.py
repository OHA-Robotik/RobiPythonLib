import machine

class BaseDriver():
    ...

class I2C_BaseDriver(BaseDriver):
    SUPPORTED_ADDRESSES = set()

    def __init__(self, i2c_interface: machine.I2C, i2c_addr: int) -> None:
        super().__init__()
        self.i2c_interface = i2c_interface
        self.i2c_addr = i2c_addr

class SPI_BaseDriver(BaseDriver):
    def __init__(self, spi_interface: machine.SPI, cs_pin: machine.Pin) -> None:
        super().__init__()
        self.spi_interface = spi_interface
        self.cs_pin = cs_pin
