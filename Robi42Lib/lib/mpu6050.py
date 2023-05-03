# Source: https://how2electronics.com/interfacing-mpu6050-with-raspberry-pi-pico-micropython/

from machine import I2C
import utime
import math


class MPU6050:

    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    TEMP_OUT_H = 0x41
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    def __init__(self, i2c: I2C, address=0x68) -> None:
        self.i2c = i2c
        self.address = address
        i2c.writeto_mem(address, self.PWR_MGMT_1, b"\x00")
        utime.sleep_ms(100)
        i2c.writeto_mem(address, self.SMPLRT_DIV, b"\x07")
        i2c.writeto_mem(address, self.CONFIG, b"\x00")
        i2c.writeto_mem(address, self.GYRO_CONFIG, b"\x00")
        i2c.writeto_mem(address, self.ACCEL_CONFIG, b"\x00")

    def read_raw_data(self, addr):
        high = self.i2c.readfrom_mem(self.address, addr, 1)[0]
        low = self.i2c.readfrom_mem(self.address, addr + 1, 1)[0]
        value = high << 8 | low
        if value > 32768:
            value -= 65536
        return value

    def get_temperature(self):
        return self.read_raw_data(self.TEMP_OUT_H) / 340.0 + 36.53

    def get_acceleration(self):
        return (
            self.read_raw_data(self.ACCEL_XOUT_H) / 16384.0,
            self.read_raw_data(self.ACCEL_XOUT_H + 2) / 16384.0,
            self.read_raw_data(self.ACCEL_XOUT_H + 4) / 16384.0,
        )

    def get_gyro(self):
        return (
            self.read_raw_data(self.GYRO_XOUT_H) / 131.0,
            self.read_raw_data(self.GYRO_XOUT_H + 2) / 131.0,
            self.read_raw_data(self.GYRO_XOUT_H + 4) / 131.0,
        )

    def get_data(self):
        accel = self.get_acceleration()
        gyro = self.get_gyro()

        return {
            "temp": self.get_temperature(),
            "accel": {
                "x": accel[0],
                "y": accel[1],
                "z": accel[2],
            },
            "gyro": {
                "x": gyro[0],
                "y": gyro[1],
                "z": gyro[2],
            },
        }

    def calculate_tilt_angles(self, accel_x, accel_y, accel_z):
        tilt_x = (
            math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * 180 / math.pi
        )
        tilt_y = (
            math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 180 / math.pi
        )
        tilt_z = (
            math.atan2(accel_z, math.sqrt(accel_x**2 + accel_y**2)) * 180 / math.pi
        )

        return tilt_x, tilt_y, tilt_z

    def get_pitch(self, pitch, gyro, dt, alpha=0.98):
        x, y, z = gyro
        pitch += x * dt

        pitch = (
            alpha * pitch
            + (1 - alpha)
            * math.atan2(
                y,
                math.sqrt(x**2 + z**2),
            )
            * 180
            / math.pi
        )
        return pitch

    def get_roll(self, roll, gyro, dt, alpha=0.98):
        x, y, z = gyro
        roll -= y * dt
        roll = (
            alpha * roll
            + (1 - alpha)
            * math.atan2(
                -x,
                math.sqrt(y**2 + z**2),
            )
            * 180
            / math.pi
        )
        return roll
