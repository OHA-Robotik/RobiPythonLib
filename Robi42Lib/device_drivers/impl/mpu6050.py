# Stolen from: https://github.com/micropython-IMU/micropython-mpu9x50/blob/master/imu.py
# Refactored by me

from utime import sleep_ms
from machine import I2C
from Robi42Lib.device_drivers.impl import base_driver
from ...abstract.vector3d import Vector3d


class MPUException(OSError):
    """
    Exception for MPU devices
    """

    pass


def bytes_toint(msb, lsb):
    """
    Convert two bytes to signed integer (big endian)
    for little endian reverse msb, lsb arguments
    Can be used in an interrupt handler
    """
    if not msb & 0x80:
        return msb << 8 | lsb  # +ve
    return -(((msb ^ 255) << 8) | (lsb ^ 255) + 1)


class MPU6050(base_driver.I2C_BaseDriver):
    """
    Module for InvenSense IMUs. Base class implements MPU6050 6DOF sensor, with
    features common to MPU9150 and MPU9250 9DOF sensors.
    """

    _I2Cerror = "I2C failure when communicating with IMU"
    SUPPORTED_ADDRESSES = {0x68}

    def __init__(
        self, i2c_interface: I2C, i2c_addr, transposition=(0, 1, 2), scaling=(1, 1, 1)
    ):

        super().__init__(i2c_interface, i2c_addr)

        self._accel = Vector3d(transposition, scaling, self._accel_callback)
        self._gyro = Vector3d(transposition, scaling, self._gyro_callback)
        self.buf1 = bytearray(1)  # Pre-allocated buffers for reads: allows reads to
        self.buf2 = bytearray(2)  # be done in interrupt handlers
        self.buf3 = bytearray(3)
        self.buf6 = bytearray(6)

        sleep_ms(200)  # Ensure PSU and device have settled

        # Can communicate with chip. Set it up.
        self.wake()  # wake it up
        self.passthrough = True  # Enable mag access from main I2C bus
        self.accel_range = 0  # default to the highest sensitivity
        self.gyro_range = 0  # Likewise for gyro

    # read from device
    def _read(
        self, buf, memaddr, addr
    ):  # addr = I2C device address, memaddr = memory location within the I2C device
        """
        Read bytes to pre-allocated buffer Caller traps OSError.
        """
        try:
            self.i2c_interface.readfrom_mem_into(addr, memaddr, buf)
        except OSError:
            raise MPUException(self._I2Cerror)

    # write to device
    def _write(self, data, memaddr, addr):
        """
        Perform a memory write. Caller should trap OSError.
        """
        self.buf1[0] = data
        try:
            self.i2c_interface.writeto_mem(addr, memaddr, self.buf1)
        except OSError:
            raise MPUException(self._I2Cerror)

    # wake
    def wake(self):
        """
        Wakes the device.
        """
        self._write(0x01, 0x6B, self.i2c_addr)  # Use best clock source
        return "awake"

    # mode
    def sleep(self):
        """
        Sets the device to sleep mode.
        """
        self._write(0x40, 0x6B, self.i2c_addr)
        return "asleep"

    @property
    def sensors(self):
        """
        returns sensor objects accel, gyro
        """
        return self._accel, self._gyro

    # get temperature
    @property
    def temperature(self):
        """
        Returns the temperature in degree C.
        """
        self._read(self.buf2, 0x41, self.i2c_addr)
        return bytes_toint(self.buf2[0], self.buf2[1]) / 340 + 35  # I think

    # passthrough
    @property
    def passthrough(self):
        """
        Returns passthrough mode True or False
        """
        self._read(self.buf1, 0x37, self.i2c_addr)
        return self.buf1[0] & 0x02 > 0

    @passthrough.setter
    def passthrough(self, mode):
        """
        Sets passthrough mode True or False
        """

        assert type(mode) is bool, "pass either True or False"

        val = 2 if mode else 0
        self._write(val, 0x37, self.i2c_addr)  # I think this is right.
        self._write(0x00, 0x6A, self.i2c_addr)

    # sample rate. Not sure why you'd ever want to reduce this from the default.
    @property
    def sample_rate(self):
        """
        Get sample rate as per Register Map document section 4.4
        SAMPLE_RATE= Internal_Sample_Rate / (1 + rate)
        default rate is zero i.e. sample at internal rate.
        """
        self._read(self.buf1, 0x19, self.i2c_addr)
        return self.buf1[0]

    @sample_rate.setter
    def sample_rate(self, rate):
        """
        Set sample rate as per Register Map document section 4.4
        """

        assert rate >= 0 or rate <= 255, "Rate must be in range 0-255"

        self._write(rate, 0x19, self.i2c_addr)

    # Low pass filters. Using the filter_range property of the MPU9250 is
    # harmless but gyro_filter_range is preferred and offers an extra setting.
    @property
    def filter_range(self):
        """
        Returns the gyro and temperature sensor low pass filter cutoff frequency
        Pass:               0   1   2   3   4   5   6
        Cutoff (Hz):        250 184 92  41  20  10  5
        Sample rate (KHz):  8   1   1   1   1   1   1
        """
        self._read(self.buf1, 0x1A, self.i2c_addr)
        res = self.buf1[0] & 7
        return res

    @filter_range.setter
    def filter_range(self, filt):
        """
        Sets the gyro and temperature sensor low pass filter cutoff frequency
        Pass:               0   1   2   3   4   5   6
        Cutoff (Hz):        250 184 92  41  20  10  5
        Sample rate (KHz):  8   1   1   1   1   1   1
        """
        # set range

        assert 0 <= filt < 7, "Filter coefficient must be between 0 and 6"

        self._write(filt, 0x1A, self.i2c_addr)

    # accelerometer range
    @property
    def accel_range(self):
        """
        Accelerometer range
        Value:              0   1   2   3
        for range +/-:      2   4   8   16  g
        """
        self._read(self.buf1, 0x1C, self.i2c_addr)
        ari = self.buf1[0] // 8
        return ari

    @accel_range.setter
    def accel_range(self, accel_range):
        """
        Set accelerometer range
        Pass:               0   1   2   3
        for range +/-:      2   4   8   16  g
        """
        ar_bytes = (0x00, 0x08, 0x10, 0x18)

        assert 0 <= accel_range < len(ar_bytes), "accel_range can only be 0, 1, 2 or 3"

        self._write(ar_bytes[accel_range], 0x1C, self.i2c_addr)

    # gyroscope range
    @property
    def gyro_range(self):
        """
        Gyroscope range
        Value:              0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        """
        # set range
        self._read(self.buf1, 0x1B, self.i2c_addr)
        gri = self.buf1[0] // 8
        return gri

    @gyro_range.setter
    def gyro_range(self, gyro_range):
        """
        Set gyroscope range
        Pass:               0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        """
        gr_bytes = (0x00, 0x08, 0x10, 0x18)

        assert 0 <= gyro_range < len(gr_bytes), "gyro_range can only be 0, 1, 2 or 3"

        self._write(
            gr_bytes[gyro_range], 0x1B, self.i2c_addr
        )  # Sets fchoice = b11 which enables filter

    # Accelerometer
    @property
    def accel(self):
        """
        Accelerometer object
        """
        return self._accel

    def _accel_callback(self):
        """
        Update accelerometer Vector3d object
        """

        self.get_accel_irq()
        scale = (16384, 8192, 4096, 2048)
        self._accel._vector[0] = self._accel._ivector[0] / scale[self.accel_range]
        self._accel._vector[1] = self._accel._ivector[1] / scale[self.accel_range]
        self._accel._vector[2] = self._accel._ivector[2] / scale[self.accel_range]

    def get_accel_irq(self):
        """
        For use in interrupt handlers. Sets self._accel._ivector[] to signed
        unscaled integer accelerometer values
        """
        self._read(self.buf6, 0x3B, self.i2c_addr)
        self._accel._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._accel._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._accel._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])

    # Gyro
    @property
    def gyro(self):
        """
        Gyroscope object
        """
        return self._gyro

    def _gyro_callback(self):
        """
        Update gyroscope Vector3d object
        """
        self.get_gyro_irq()
        scale = (131, 65.5, 32.8, 16.4)
        self._gyro._vector[0] = self._gyro._ivector[0] / scale[self.gyro_range]
        self._gyro._vector[1] = self._gyro._ivector[1] / scale[self.gyro_range]
        self._gyro._vector[2] = self._gyro._ivector[2] / scale[self.gyro_range]

    def get_gyro_irq(self):
        """
        For use in interrupt handlers. Sets self._gyro._ivector[] to signed
        unscaled integer gyro values. Error trapping disallowed.
        """
        self._read(self.buf6, 0x43, self.i2c_addr)
        self._gyro._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._gyro._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._gyro._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])


def calculate_velocity(a, dt, v0):
    return a * dt + v0


def calculate_position(a, dt, v0, x0):
    return 0.5 * a * dt**2 + v0 * dt + x0


if __name__ == "__main__":
    from machine import Pin
    import time

    last_velocity = 0
    last_position = 0

    mpu = MPU6050(I2C(0, sda=Pin(16), scl=Pin(17), freq=400000), 0x68)

    # start_time = time.time()
    # mpu.accel.calibrate(lambda: time.time() - start_time > 5 * 60)
    # print(mpu.accel.cal)
    mpu.accel.cal = (-0.02697754, -0.002563477, -0.8944092)

    delay = 0.05

    while True:

        acceleration = mpu.accel.z * 9.81

        if abs(acceleration) < 0.2:
            acceleration = 0

        velocity = calculate_velocity(acceleration, delay, last_velocity)
        last_velocity = velocity
        position = calculate_position(acceleration, delay, velocity, last_position)
        last_position = position

        if acceleration >= 0:
            print(
                f" {acceleration:.03f}m/s^2 {velocity:.03f}m/s {position:.03f}m",
                end=" " * 10 + "\r",
            )
        else:
            print(
                f"{acceleration:.03f}m/s^2 {velocity:.03f}m/s {position:.03f}m",
                end=" " * 10 + "\r",
            )
        sleep_ms(int(delay * 1000))
