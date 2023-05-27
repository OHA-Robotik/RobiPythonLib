

class BaseDriver():
    ...

class I2C_BaseDriver(BaseDriver):
    SUPPORTED_ADDRESSES = set()

    def __init__(self, i2c_interface, i2c_addr) -> None:
        super().__init__()
        self.i2c_interface = i2c_interface
        self.i2c_addr = i2c_addr

class SPI_BaseDriver(BaseDriver):
    ...
