# https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/README.md

import asyncio
import random

import aioble
import bluetooth
import time


class Bluetooth:

    def __init__(self, services: list[aioble.Service], advertising_name: str = "Robi 42"):

        self.services = services
        self.advertising_name = advertising_name

        self._ADV_APPEARANCE_GENERIC_ROBOT = 4242

        # How frequently to send advertising beacons.
        # If the environment has multiple devices, slightly randomizing the ADV_INTERVAL_MS can reduce advertisement collisions
        self._ADV_INTERVAL_MS = 250_000 + random.randint(0, 50_000)

        self._bt_connected = False
        self._run_advertising = False

    def begin(self):
        aioble.register_services(*self.services)

    def start_advertising(self):
        self._run_advertising = True
        asyncio.create_task(self._advertise())

    def stop_advertising(self):
        self._run_advertising = False

    @staticmethod
    def write_data_to_characteristic(characteristic: aioble.Characteristic, data: bytes):
        characteristic.write(data, send_update=True)

    async def _advertise(self):
        while self._run_advertising:
            print("Waiting for connection")
            async with await aioble.advertise(
                self._ADV_INTERVAL_MS,
                name=self.advertising_name,
                services=[service.uuid for service in self.services],
                appearance=self._ADV_APPEARANCE_GENERIC_ROBOT,
            ) as connection:
                print("Connection from", connection.device)
                self._bt_connected = True
                await connection.disconnected(timeout_ms=None)
                self._bt_connected = False
                print("Lost bluetooth connection")

    async def wait_for_connection(self):
        while not self._bt_connected:
            await asyncio.sleep(0.1)

    @property
    def is_connected(self):
        return self._bt_connected


async def _example():

    SERVICE_UUID = bluetooth.UUID(0xC0FE)
    TEST_DATA_UUID = bluetooth.UUID(0xBEEF)

    sensor_service = aioble.Service(SERVICE_UUID)
    sensor_characteristic = aioble.Characteristic(
        sensor_service, TEST_DATA_UUID, read=True, notify=True
    )

    test_ble = Bluetooth([sensor_service])

    test_ble.start_advertising()

    await test_ble.wait_for_connection()

    i = 0
    while True:
        test_ble.write_data_to_characteristic(sensor_characteristic, b"Hello %d" % i)
        await asyncio.sleep(1)
        i += 1


if __name__ == "__main__":
    asyncio.run(_example())
