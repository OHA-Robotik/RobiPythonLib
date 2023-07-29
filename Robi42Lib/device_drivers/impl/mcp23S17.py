from machine import SPI, Pin

from . import base_driver


class MCP23S17(base_driver.SPI_BaseDriver):

    DIR_INPUT = 1
    DIR_OUTPUT = 0
    PULLUP_ENABLED = 1
    PULLUP_DISABLED = 0
    LEVEL_LOW = 0
    LEVEL_HIGH = 1

    # Register addresses (ICON.BANK = 0) as documentined in the technical data sheet at
    # http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf
    MCP23S17_IODIRA = 0
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

    # Bit field flags as documentined in the technical data sheet at
    # http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf
    IOCON_UNUSED = 0x01
    IOCON_INTPOL = 0x02
    IOCON_ODR = 0x04
    IOCON_HAEN = 0x08
    IOCON_DISSLW = 0x10
    IOCON_SEQOP = 0x20
    IOCON_MIRROR = 0x40
    IOCON_BANK_MODE = 0x80

    IOCON_INIT = 0  # IOCON_BANK_MODE = 0, IOCON_HAEN = 0 address pins disabled

    MCP23S17_CMD_WRITE = 0x40
    MCP23S17_CMD_READ = 0x41

    def __init__(self, spi_interface: SPI, cs: Pin, deviceID: int):
        """
        Constructor
        Initializes all attributes with 0.
        Keyword arguments:
        bus -- The SPI bus number
        ce -- The chip-enable number for the SPI
        deviceID -- The device ID of the component, i.e., the hardware address (default 0.0)
        """
        super().__init__(spi_interface, cs)
        self._GPIOA = 0
        self._GPIOB = 0
        self._IODIRA = 0xFF
        self._IODIRB = 0xFF
        self._GPPUA = 0
        self._GPPUB = 0
        self.is_initialized = False
        self.read_command = MCP23S17.MCP23S17_CMD_READ | (deviceID << 1)
        self.write_command = MCP23S17.MCP23S17_CMD_WRITE | (deviceID << 1)
        self.port_a_pullup_status = 0
        self.port_b_pullup_status = 0

    def open(self):
        """
        Initializes the MCP23S17 with hardware-address access
        and sequential operations' mode.
        """
        self.is_initialized = True

        self._write_register(MCP23S17.MCP23S17_IOCON, MCP23S17.IOCON_INIT)
        self._write_register(MCP23S17.MCP23S17_IOCON, MCP23S17.IOCON_HAEN)

    def close(self):
        """Closes the SPI connection that the MCP23S17 component is using."""
        self.is_initialized = False

    def set_direction(self, pin: int, direction: bool):
        """
        Sets the direction for a given pin.
        Parameters:
        pin -- The pin index (0 - 15)
        direction -- The direction of the pin (MCP23S17.DIR_INPUT, MCP23S17.DIR_OUTPUT)
        """
        assert pin < 16 and self.is_initialized

        if pin < 8:
            register = MCP23S17.MCP23S17_IODIRA
            data = self._IODIRA
            noshifts = pin
        else:
            register = MCP23S17.MCP23S17_IODIRB
            data = self._IODIRB
            noshifts = pin & 0x07

        if direction:
            data |= 1 << noshifts
        else:
            data &= ~(1 << noshifts)

        self._write_register(register, data)

        if pin < 8:
            self._IODIRA = data
        else:
            self._IODIRB = data

    def set_pullup(self, pin: int, enable: bool):
        # first find if the pin num is in port a or b, then build the right bitmask
        if pin < 8:  # 0-7 is PORT_A
            if enable:
                bitmask = self.port_a_pullup_status | (1 << pin)
            else:
                bitmask = self.port_a_pullup_status & (0xFF ^ (1 << pin))
            self.set_pullup_PORTA(bitmask)
        else:  # 8-15 is PORT_B
            if enable:
                bitmask = self.port_a_pullup_status | (1 << (pin - 8))
            else:
                bitmask = self.port_a_pullup_status & (0xFF ^ (1 << (pin - 8)))
            self.set_pullup_PORTB(bitmask)

    def digital_read(self, pin: int) -> bool:
        """
        Reads the logical level of a given pin.
        Parameters:
        pin -- The pin index (0 - 15)
        Returns:
         - MCP23S17.LEVEL_LOW, if the logical level of the pin is low,
         - MCP23S17.LEVEL_HIGH, otherwise.
        """
        assert self.is_initialized and pin < 16

        if pin < 8:
            self._GPIOA = self._read_register(MCP23S17.MCP23S17_GPIOA)
            return (self._GPIOA & (1 << pin)) != 0

        self._GPIOB = self._read_register(MCP23S17.MCP23S17_GPIOB)
        pin &= 0x07
        return (self._GPIOB & (1 << pin)) != 0

    def digital_write(self, pin: int, level: bool):
        """
        Sets the level of a given pin.
        Parameters:
        pin -- The pin idnex (0 - 15)
        level -- The logical level to be set (MCP23S17.LEVEL_LOW, MCP23S17.LEVEL_HIGH)
        """
        assert self.is_initialized and pin < 16

        if pin < 8:
            register = MCP23S17.MCP23S17_GPIOA
            data = self._GPIOA
            noshifts = pin
        else:
            register = MCP23S17.MCP23S17_GPIOB
            noshifts = pin & 0b111
            data = self._GPIOB

        if level:
            data |= 1 << noshifts
        else:
            data &= ~(1 << noshifts)

        self._write_register(register, data)

        if pin < 8:
            self._GPIOA = data
        else:
            self._GPIOB = data

    def set_dir_PORTA(self, data):
        assert self.is_initialized

        self._write_register(MCP23S17.MCP23S17_IODIRA, data)
        self._IODIRA = data

    def set_dir_PORTB(self, data):
        assert self.is_initialized

        self._write_register(MCP23S17.MCP23S17_IODIRB, data)
        self._IODIRA = data

    def set_pullup_PORTA(self, data):
        assert self.is_initialized
        self.port_a_pullup_status = data

        self._write_register(MCP23S17.MCP23S17_GPPUA, data)
        self._GPPUA = data

    def set_pullup_PORTB(self, data):
        assert self.is_initialized
        self.port_b_pullup_status = data

        self._write_register(MCP23S17.MCP23S17_GPPUB, data)
        self._GPPUB = data

    def read_PORTA(self):
        assert self.is_initialized

        data = self._read_register(MCP23S17.MCP23S17_GPIOA)
        self._GPIOA = data
        return data

    def read_PORTB(self):
        assert self.is_initialized

        data = self._read_register(MCP23S17.MCP23S17_GPIOB)
        self._GPIOB = data
        return data

    def write_PORTA(self, data):
        assert self.is_initialized

        self._write_register(MCP23S17.MCP23S17_GPIOA, data)
        self._GPIOA = data

    def write_PORTB(self, data):
        assert self.is_initialized

        self._write_register(MCP23S17.MCP23S17_GPIOB, data)
        self._GPIOB = data

    def write_GPIO(self, data):
        """Sets the data port value for all pins.
        Parameters:
        data - The 16-bit value to be set.
        """
        assert self.is_initialized

        self._GPIOA = data & 0xFF
        self._GPIOB = data >> 8
        self._write_register_word(MCP23S17.MCP23S17_GPIOA, data)

    def read_GPIO(self):
        """Reads the data port value of all pins.
        Returns:
         - The 16-bit data port value
        """
        assert self.is_initialized

        data = self._read_register_word(MCP23S17.MCP23S17_GPIOA)
        self._GPIOA = data & 0xFF
        self._GPIOB = data >> 8
        return data

    def _write_register(self, register, value):
        assert self.is_initialized

        self.cs_pin.off()
        self.spi_interface.write(bytearray([self.write_command, register, value]))
        self.cs_pin.on()

    def _read_register(self, register):
        assert self.is_initialized

        self.cs_pin.off()
        self.spi_interface.write(bytearray([self.read_command, register]))
        data = self.spi_interface.read(1)
        self.cs_pin.on()
        return data[0]

    def _read_register_word(self, register):
        assert self.is_initialized

        buffer = [self._read_register(register), self._read_register(register + 1)]
        return (buffer[1] << 8) | buffer[0]

    def _write_register_word(self, register, data):
        assert self.is_initialized

        self._write_register(register, data & 0xFF)
        self._write_register(register + 1, data >> 8)
