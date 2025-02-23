import asyncio

from Robi42Lib import Robi42
from Robi42Lib.modules.ble import Bluetooth
from Robi42Lib.rsrc.impl.rsrc_handshake import RSRCHandshake
import bluetooth
import aioble


class RobiLive:

    def __init__(self, robi: Robi42, update_delay_ms: int = 100):
        self.robi = robi
        self.update_delay_ms = update_delay_ms
        self._send_data = False
        self._advertise = False

        rsrc_service_uuid = bluetooth.UUID(0x2579)
        rsrc_characteristic_uuid = bluetooth.UUID(0x8765)
        start_confirmation_characteristic_uuid = bluetooth.UUID(0x4234)
        rsrc_handshake_characteristic_uuid = bluetooth.UUID(0x4744)

        sensors_service = aioble.Service(rsrc_service_uuid)
        self.rsrc_characteristic = aioble.Characteristic(
            sensors_service, rsrc_characteristic_uuid, read=True, notify=True
        )
        self.rsrc_handshake_characteristic = aioble.Characteristic(
            sensors_service, rsrc_handshake_characteristic_uuid, read=True
        )
        self.start_confirmation_characteristic = aioble.Characteristic(
            sensors_service, start_confirmation_characteristic_uuid, write=True
        )

        self.ble = Bluetooth([sensors_service])

    def start(self):
        self._send_data = True
        self._advertise = True
        asyncio.create_task(self._run())

    def stop_sending(self):
        self._send_data = False

    def stop(self):
        self._send_data = False
        self._advertise = False

    async def _wait_for_disconnection(self, connection):
        await connection.disconnected(timeout_ms=None)
        print("Disconnected, stop sending data")
        self.stop_sending()

    async def _await_start_confirmation(self):
        await self.start_confirmation_characteristic.written()

    async def _run(self):

        while self._advertise:

            print("Waiting for connection")

            connection = await self.ble.advertise_and_wait_for_connection()

            print("Connected")

            asyncio.create_task(self._wait_for_disconnection(connection))

            print("Sending RSRC handshake")

            self.ble.write_data_to_characteristic(
                self.rsrc_handshake_characteristic,
                RSRCHandshake(protocol_version=1, msdt=10).as_bytes(),
                send_update=False,
            )

            print("Waiting for start confirmation")

            await self._await_start_confirmation()

            print("Start confirmed")

            frame_id = 0
            while self._send_data:

                sampled_state = self.robi.sample_state(frame_id)

                self.ble.write_data_to_characteristic(
                    self.rsrc_characteristic, sampled_state.as_bytes()
                )

                # TODO: Sample and send data in background

                await asyncio.sleep(self.update_delay_ms / 1000)

                frame_id += 1

    @property
    def is_running(self):
        return self._send_data or self._advertise


async def main():
    robi = Robi42()
    robi_live = RobiLive(robi)
    robi_live.start()

    while robi_live.is_running:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
