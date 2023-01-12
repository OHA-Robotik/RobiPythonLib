from machine import Pin, SPI


class MCP23S17:

    DIR_INPUT = 1
    DIR_OUTPUT = 0

    SPI_INTCONA = 0x08
    SPI_IODIRA = 0x00
    SPI_IODIRB = 0x01
    SPI_GPIO_A = 0x12
    SPI_GPIO_B = 0x13

    MCP23S17_IODIRA = 0x00
    MCP23S17_IODIRB = 0x01
    MCP23S17_IPOLA = 0x02
    MCP23S17_IPOLB = 0x03
    MCP23S17_GPIOA = 0x12
    MCP23S17_GPIOB = 0x13
    MCP23S17_OLATA = 0x14
    MCP23S17_OLATB = 0x15
    MCP23S17_IOCON = 0x0A
    MCP23S17_GPPUA = 0x0C
    MCP23S17_GPPUB = 0x0D

    """Bit field flags as documentined in the technical data sheet at
    http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf
    """
    IOCON_UNUSED = 0x01
    IOCON_INTPOL = 0x02
    IOCON_ODR = 0x04
    IOCON_HAEN = 0x08
    IOCON_DISSLW = 0x10
    IOCON_SEQOP = 0x20
    IOCON_MIRROR = 0x40
    IOCON_BANK_MODE = 0x80

    IOCON_INIT = 0x00  # IOCON_BANK_MODE = 0, IOCON_HAEN = 0 address pins disabled

    MCP23S17_CMD_WRITE = 0x40
    MCP23S17_CMD_READ = 0x41

    def __init__(self, cs: Pin, device_id: int, spi_interface: SPI) -> None:
        self.cs = cs
        self.spi = spi_interface
        self.is_open = False
        self.write_command = self.MCP23S17_CMD_WRITE | (device_id << 1)
        self.read_command = self.MCP23S17_CMD_READ | (device_id << 1)

        self._GPIOA = 0x00
        self._GPIOB = 0x00
        self._IODIRA = 0xFF
        self._IODIRB = 0xFF
        self._GPPUA = 0x00
        self._GPPUB = 0x00

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

    def digital_read(self, pin: int):
        assert self.is_open and pin < 16

        if pin < 8:
            self._GPIOA = self.read_register(self.MCP23S17_GPIOA)
            return int((self._GPIOA & (1 << pin)) != 0)

        self._GPIOB = self.read_register(self.MCP23S17_GPIOB)
        pin &= 0x07
        return int((self._GPIOB & (1 << pin)) != 0)

    def write_register(self, register: int, value):
        assert self.is_open

        self.cs.off()
        self.spi.write(bytearray([self.write_command, register, value]))
        self.cs.on()

    def read_register(self, register: int) -> int:
        assert self.is_open

        self.cs.off()
        txdata = bytearray([self.read_command, register, 0])
        rxdata = bytearray(len(txdata))
        self.spi.write_readinto(txdata, rxdata)
        self.cs.on()

        return rxdata[2]
