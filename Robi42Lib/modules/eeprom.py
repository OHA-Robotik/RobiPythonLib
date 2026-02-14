import struct
from . import base_module
from ..device_drivers.impl import eeprom_i2c


# --- Custom Exceptions ---
class EEPROMError(Exception):
    """Base exception for EEPROM errors."""
    pass


class AddressOutOfBoundsError(EEPROMError):
    """Raised when attempting to access an address outside valid range."""
    pass


# --- Base EEPROM Implementation ---
class EEPROM(base_module.BaseModule):

    def _read_bytes_impl(self, start_addr: int, length: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver) -> bytearray:
        return driver[start_addr:start_addr + length]

    def _read_byte_impl(self, addr: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver) -> int:
        return driver[addr]

    def _write_byte_impl(self, addr: int, value: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver):
        driver[addr] = value

    def _write_bytes_impl(self, start_addr: int, data: bytearray, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver):
        driver[start_addr:start_addr + len(data)] = data

    # --- Public API with Hardware Injection ---

    @base_module.get_first_i2c_hardware('EEPROM_24LC256_I2C_driver')
    def read_bytes(self, start_addr: int, length: int,
                   EEPROM_24LC256_I2C_driver: eeprom_i2c.EEPROM_24LC256_I2C_driver = None) -> bytearray:
        return self._read_bytes_impl(start_addr, length, EEPROM_24LC256_I2C_driver)

    @base_module.get_first_i2c_hardware('EEPROM_24LC256_I2C_driver')
    def read_byte(self, addr: int, EEPROM_24LC256_I2C_driver: eeprom_i2c.EEPROM_24LC256_I2C_driver = None) -> int:
        return self._read_byte_impl(addr, EEPROM_24LC256_I2C_driver)

    @base_module.get_first_i2c_hardware('EEPROM_24LC256_I2C_driver')
    def write_byte(self, addr: int, value: int, EEPROM_24LC256_I2C_driver: eeprom_i2c.EEPROM_24LC256_I2C_driver = None):
        self._write_byte_impl(addr, value, EEPROM_24LC256_I2C_driver)

    @base_module.get_first_i2c_hardware('EEPROM_24LC256_I2C_driver')
    def write_bytes(self, start_addr: int, data: bytearray,
                    EEPROM_24LC256_I2C_driver: eeprom_i2c.EEPROM_24LC256_I2C_driver = None):
        self._write_bytes_impl(start_addr, data, EEPROM_24LC256_I2C_driver)

    @base_module.get_first_i2c_hardware('EEPROM_24LC256_I2C_driver')
    def is_connected(self, EEPROM_24LC256_I2C_driver: eeprom_i2c.EEPROM_24LC256_I2C_driver = None):
        return EEPROM_24LC256_I2C_driver is not None

    # --- Data Type Helpers ---

    def write_str(self, start_addr: int, string: str, encoding: str = 'utf-8'):
        # We append a null terminator or store length? 
        # Standard generic EEPROM write usually just writes bytes.
        self.write_bytes(start_addr, bytearray(string.encode(encoding)))

    def read_str(self, start_addr: int, length: int, encoding: str = 'utf-8') -> str:
        return self.read_bytes(start_addr, length).decode(encoding)

    def write_int(self, start_addr: int, length: int, value: int, byteorder: str = 'big', signed: bool = False):
        self.write_bytes(start_addr, bytearray(value.to_bytes(length, byteorder, signed=signed)))

    def read_int(self, start_addr: int, length: int, byteorder: str = 'big', signed: bool = True) -> int:
        data = self.read_bytes(start_addr, length)
        # MicroPython int.from_bytes may not support 'signed' keyword in older versions
        # logic provided in prompt preserved
        value = int.from_bytes(data, byteorder)

        if signed:
            bits = length * 8
            if value & (1 << (bits - 1)):  # if sign bit set
                value -= 1 << bits
        return value

    def write_int32(self, start_addr: int, value: int):
        self.write_int(start_addr, 4, value)

    def read_int32(self, start_addr: int) -> int:
        return self.read_int(start_addr, 4)

    def write_float(self, start_addr: int, value: float):
        """Writes a standard IEEE 754 float (4 bytes)."""
        data = struct.pack('>f', value)  # Big-endian float
        self.write_bytes(start_addr, bytearray(data))

    def read_float(self, start_addr: int) -> float:
        """Reads a standard IEEE 754 float (4 bytes)."""
        data = self.read_bytes(start_addr, 4)
        return struct.unpack('>f', data)[0]

    def fill(self, start_addr: int, length: int, value: int = 0xFF):
        """Fills a region with a specific byte value (default 0xFF for erase)."""
        # Create chunks to avoid allocating huge bytearrays for large fills
        chunk_size = 32
        chunk = bytearray([value] * chunk_size)

        remaining = length
        current_addr = start_addr

        while remaining > 0:
            write_len = min(remaining, chunk_size)
            self.write_bytes(current_addr, chunk[:write_len])
            current_addr += write_len
            remaining -= write_len


# --- Partition Implementation ---
class Partition(EEPROM):

    def __init__(self, partition_start_addr: int, partition_size: int):
        self._offset = partition_start_addr
        self._size = partition_size
        if self._offset < 0 or self._size < 0:
            raise ValueError("Partition offset and size must be non-negative.")

    @staticmethod
    def from_end_addr(start_addr: int, end_addr: int) -> 'Partition':
        return Partition(start_addr, end_addr - start_addr)

    @property
    def size(self) -> int:
        return self._size

    @property
    def start_addr(self) -> int:
        return self._offset

    @property
    def end_addr(self) -> int:
        return self._offset + self._size

    def _validate_range(self, start_addr: int, length: int = 1):
        """Helper to validate if the operation stays within partition bounds."""
        if start_addr < 0:
            raise AddressOutOfBoundsError(f"Address {start_addr} cannot be negative.")

        if start_addr + length > self.size:
            raise AddressOutOfBoundsError(
                f"Operation out of bounds: Addr {start_addr} + Len {length} > Partition Size {self.size}"
            )

    # -- Overrides to inject offset and check bounds --

    def _read_bytes_impl(self, start_addr: int, length: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver) -> bytearray:
        self._validate_range(start_addr, length)
        return super()._read_bytes_impl(self.start_addr + start_addr, length, driver)

    def _read_byte_impl(self, addr: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver) -> int:
        self._validate_range(addr, 1)
        return super()._read_byte_impl(self.start_addr + addr, driver)

    def _write_byte_impl(self, addr: int, value: int, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver):
        self._validate_range(addr, 1)
        super()._write_byte_impl(self.start_addr + addr, value, driver)

    def _write_bytes_impl(self, start_addr: int, data: bytearray, driver: eeprom_i2c.EEPROM_24LC256_I2C_driver):
        self._validate_range(start_addr, len(data))
        super()._write_bytes_impl(self.start_addr + start_addr, data, driver)


# --- External Storage Manager ---
class ExternalStorage(base_module.BaseModule):
    _TOTAL_SIZE = 0x40000  # 256 KiB   hardcoding for now
    _SYSTEM_RESERVED_SPACE = 10 * 1024  # 10 KiB
    _SYSTEM_RESERVED_START_ADDR = 0

    class SpecialSystemAddresses:
        HwRevision = 0
        SerialNumber = 1  # Example: Reserved 1-16 for serial
        BootCount = 17  # Example: 4 bytes for boot count

    def __init__(self):
        self._system_partition = Partition(self._SYSTEM_RESERVED_START_ADDR, self._SYSTEM_RESERVED_SPACE)
        self._user_partition = Partition.from_end_addr(self._system_partition.end_addr, self._TOTAL_SIZE)

    def is_connected(self) -> bool:
        return self._system_partition.is_connected()

    # -- System Accessors --

    def read_hw_revision(self) -> int:
        return self._system_partition.read_byte(self.SpecialSystemAddresses.HwRevision)

    def write_hw_revision(self, revision: int):
        # Usually system info is write-once or protected, but allowing write for now
        self._system_partition.write_byte(self.SpecialSystemAddresses.HwRevision, revision)

    # -- User Storage Accessors --

    def write_byte(self, addr: int, value: int):
        self._user_partition.write_byte(addr, value)

    def read_byte(self, addr: int) -> int:
        return self._user_partition.read_byte(addr)

    def write_bytes(self, addr: int, data: bytearray):
        self._user_partition.write_bytes(addr, data)

    def read_bytes(self, addr: int, length: int) -> bytearray:
        return self._user_partition.read_bytes(addr, length)

    def wipe_user_data(self):
        """Erases the entire user partition."""
        self._user_partition.fill(0, self._user_partition.size, 0xFF)

    @property
    def user_capacity(self) -> int:
        return self._user_partition.size
