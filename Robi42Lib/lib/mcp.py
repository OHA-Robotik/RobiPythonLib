from machine import Pin, SPI


class MCP23S17:

    DIR_INPUT = 1
    DIR_OUTPUT = 0

    MCP23S17_IODIRA = 0
    MCP23S17_IODIRB = 1
    MCP23S17_GPIOA = 0x12
    MCP23S17_GPIOB = 0x13
    MCP23S17_IOCON = 0x0A

    IOCON_INIT = 0

    MCP23S17_CMD_WRITE = 0x40
    MCP23S17_CMD_READ = 0x41

    def __init__(self, cs: Pin, device_id: int, spi_interface: SPI) -> None:
        self.cs = cs
        self.spi = spi_interface
        self.is_open = False
        self.write_command = self.MCP23S17_CMD_WRITE | (device_id << 1)
        self.read_command = self.MCP23S17_CMD_READ | (device_id << 1)

        self._GPIOA = 0
        self._GPIOB = 0
        self._IODIRA = 0xFF
        self._IODIRB = 0xFF

        self.cs.on()

    def open(self):
        self.is_open = True
        self.write_register(self.MCP23S17_IOCON, self.IOCON_INIT)

    def close(self):
        self.is_open = False

    def set_direction(self, pin: int, direction: bool):
        assert self.is_open and pin < 16
        direction = bool(direction)

        if pin < 8:
            register = self.MCP23S17_IODIRA
            data = self._IODIRA
            noshifts = pin
        else:
            register = self.MCP23S17_IODIRB
            noshifts = pin & 0x07
            data = self._IODIRB

        if direction:
            data |= 1 << noshifts
        else:
            data &= ~(1 << noshifts)

        self.write_register(register, data)

        if pin < 8:
            self._IODIRA = data
        else:
            self._IODIRB = data

    def digital_write(self, pin: int, level: bool):
        assert self.is_open and pin < 16
        level = bool(level)

        if pin < 8:
            register = self.MCP23S17_GPIOA
            data = self._GPIOA
            noshifts = pin
        else:
            register = self.MCP23S17_GPIOB
            noshifts = pin & 0x07
            data = self._GPIOB

        if level:
            data |= 1 << noshifts
        else:
            data &= ~(1 << noshifts)

        self.write_register(register, data)

        if pin < 8:
            self._GPIOA = data
        else:
            self._GPIOB = data

    def digital_read(self, pin: int) -> bool:
        assert self.is_open and pin < 16

        if pin < 8:
            self._GPIOA = self.read_register(self.MCP23S17_GPIOA)
            return (self._GPIOA & (1 << pin)) != 0

        self._GPIOB = self.read_register(self.MCP23S17_GPIOB)
        pin &= 0x07
        return (self._GPIOB & (1 << pin)) != 0

    def write_register(self, register: int, value):
        assert self.is_open

        self.cs.off()
        self.spi.write(bytearray([self.write_command, register, value]))
        self.cs.on()

    def read_register(self, register: int) -> int:
        assert self.is_open

        txdata = bytearray([self.read_command, register, 0])
        rxdata = bytearray(3)
        self.cs.off()
        self.spi.write_readinto(txdata, rxdata)
        self.cs.on()

        return rxdata[0]
