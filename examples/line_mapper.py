import time
import asyncio
import aioble
import bluetooth

from Robi42Lib.robi42 import Robi42
from machine import Timer
from micropython import const

FWD = True
BWD = not FWD


# Binary file structure documentation:
# https://github.com/Finnomator/robi_line_drawer/wiki/IR-Read-Result-Binary-File-Definition


def encode_data(
    freq_left: int,
    freq_right: int,
    left_direction: bool,
    right_direction: bool,
    raw_l: int,
    raw_m: int,
    raw_r: int,
) -> bytes:
    return (
        freq_left.to_bytes(2, "big")
        + freq_right.to_bytes(2, "big")
        + (
            (int(left_direction == FWD) << 31)
            | (int(right_direction == FWD) << 30)
            | raw_l << 20
            | raw_m << 10
            | raw_r
        ).to_bytes(4, "big")
    )


class LineMapper:

    file_type_version = const(1)
    version_byte_len = const(2)
    resolution_byte_len = const(2)

    def __init__(self, robi: Robi42, resolution: float = 0.1, file_name: str = "ir_read.bin"):
        self.robi = robi
        self.resolution = resolution
        self.file_name = file_name
        self.is_running = False
        self.threshold = 200

    def _timer_callback(self, timer: Timer):
        freq_left = self.robi.motors.left.freq
        freq_right = self.robi.motors.right.freq
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()

        data = encode_data(
            freq_left,
            freq_right,
            self.robi.motors.left.direction,
            self.robi.motors.right.direction,
            raw_l,
            raw_m,
            raw_r,
        )

        try:
            self.f.write(data)
        except OSError:
            self.robi.lcd.turn_on()
            self.robi.lcd.put_str("D:")
            self.is_running = False

    def step(self, timer: Timer):
        threshold = 200
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()

        l_dark = raw_l < threshold
        m_dark = raw_m < threshold
        r_dark = raw_r < threshold

        if m_dark:
            if not l_dark and not r_dark:
                self.robi.motors.left.set_freq(5000)
                self.robi.motors.right.set_freq(5000)
            elif l_dark and not r_dark:
                self.robi.motors.left.set_freq(2000)
                self.robi.motors.right.set_freq(4000)
            elif r_dark and not l_dark:
                self.robi.motors.left.set_freq(4000)
                self.robi.motors.right.set_freq(2000)
        else:
            if l_dark and not r_dark:
                self.robi.motors.left.set_freq(300)
                self.robi.motors.right.set_freq(4000)
            elif r_dark and not l_dark:
                self.robi.motors.left.set_freq(4000)
                self.robi.motors.right.set_freq(300)

    def start(self):

        with open(self.file_name, "wb") as f:
            version_byte = self.file_type_version.to_bytes(self.version_byte_len, "big")
            resolution_byte = int(self.resolution * 1000).to_bytes(self.resolution_byte_len, "big")

            f.write(version_byte)
            f.write(resolution_byte)

        self.f = open(self.file_name, "ab")

        timer = Timer(-1)
        step_timer = Timer(-1)
        tick = int(self.resolution * 1000)
        self.is_running = True

        self.robi.motors.set_direction(FWD)
        self.robi.motors.enable()

        step_timer.init(period=tick, callback=self.step)
        timer.init(period=tick, callback=self._timer_callback)

        while self.is_running:
            if not self.robi.buttons.center.value():
                self.is_running = False
                break
            time.sleep(0.1)

        step_timer.deinit()
        timer.deinit()
        self.robi.motors.disable()
        self.f.close()


class BluetoothLineMapper(LineMapper):
    def __init__(self, robi: Robi42, resolution: float = 0.1):
        super().__init__(robi, resolution)

        # Replace with your robot's service UUID
        self._SENSOR_SERVICE_UUID = bluetooth.UUID(
            0x1234
        )  # Example UUID for robot sensor service
        # Replace with your robot's characteristic UUID
        self._SENSOR_DATA_UUID = bluetooth.UUID(
            0x5678
        )  # Example UUID for robot sensor data characteristic
        # Update appearance to something appropriate for your robot
        self._ADV_APPEARANCE_GENERIC_ROBOT = 1234  # Example appearance for robot

        # How frequently to send advertising beacons.
        self._ADV_INTERVAL_MS = 250_000

        # Register GATT server.
        self.sensor_service = aioble.Service(self._SENSOR_SERVICE_UUID)
        self.sensor_characteristic = aioble.Characteristic(
            self.sensor_service, self._SENSOR_DATA_UUID, read=True, notify=True
        )
        aioble.register_services(self.sensor_service)
        self.bt_connected = False

    def _timer_callback(self, timer: Timer):
        freq_left = self.robi.motors.left.freq
        freq_right = self.robi.motors.right.freq
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()

        data = encode_data(
            freq_left,
            freq_right,
            self.robi.motors.left.direction,
            self.robi.motors.right.direction,
            raw_l,
            raw_m,
            raw_r,
        )

        self.sensor_characteristic.write(data, send_update=True)

    async def peripheral_task(self):
        while self.is_running:
            async with await aioble.advertise(
                self._ADV_INTERVAL_MS,
                name="Robi 42",
                services=[self._SENSOR_SERVICE_UUID],
                appearance=self._ADV_APPEARANCE_GENERIC_ROBOT,
            ) as connection:
                print("Connection from", connection.device)
                self.bt_connected = True
                await connection.disconnected(timeout_ms=None)
                self.bt_connected = False
                print("Lost bluetooth connection")

    def activate_bt(self):
        asyncio.create_task(self.peripheral_task())

    async def run(self):
        timer = Timer(-1)
        step_timer = Timer(-1)
        tick = int(self.resolution * 1000)

        self.is_running = True

        self.activate_bt()
        print("Awaiting bluetooth connection")
        while not self.bt_connected:
            await asyncio.sleep(0.1)

        self.robi.motors.enable()

        step_timer.init(period=tick, callback=self.step)
        timer.init(period=tick, callback=self._timer_callback)

        while self.is_running and self.bt_connected:
            if not self.robi.buttons.center.value():
                break
            await asyncio.sleep(0.1)

        self.is_running = False

        step_timer.deinit()
        timer.deinit()
        self.robi.motors.disable()

    def start(self):
        asyncio.run(self.run())


def main():
    r = Robi42()
    r.begin()
    lm = LineMapper(r)
    lm.start()


if __name__ == "__main__":
    main()
