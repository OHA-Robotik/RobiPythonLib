import asyncio

from Robi42Lib import Robi42
from Robi42Lib.modules.ble import Bluetooth
from Robi42Lib.rsrc.impl.rsrc_handshake import RSRCHandshake
import bluetooth
import aioble


class RobiLive:

    def __init__(self, robi: Robi42, state_update_delay_ms: int = 100):
        self.robi = robi
        self.state_update_delay_ms = state_update_delay_ms

        self._send_rsrc_data = False
        self._advertise = False
        self._read_remote_control = False
        self.maximum_motor_frequency = 30_000

        self._current_velocity_value = 0.0
        self._current_steering_value = 0.5

        # Remote Control

        remote_control_service_uuid = bluetooth.UUID(0xBA73)
        velocity_characteristic_uuid = bluetooth.UUID(0x6B2F)
        steering_characteristic_uuid = bluetooth.UUID(0x3F4A)

        remote_control_service = aioble.Service(remote_control_service_uuid)
        self.velocity_characteristic = aioble.Characteristic(
            remote_control_service, velocity_characteristic_uuid, write=True
        )
        self.steering_characteristic = aioble.Characteristic(
            remote_control_service, steering_characteristic_uuid, write=True
        )

        # RSRC

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

        self.ble = Bluetooth([sensors_service, remote_control_service])

    def start(self):
        self._send_rsrc_data = True
        self._read_remote_control = True
        self._advertise = True
        asyncio.create_task(self._run())

    def stop_bluetooth_read_write(self):
        self._send_rsrc_data = False
        self._read_remote_control = False

    def stop(self):
        self._send_rsrc_data = False
        self._advertise = False
        self._read_remote_control = False
        self.robi.motors.disable()

    async def _wait_for_disconnection(self, connection):
        await connection.disconnected(timeout_ms=None)
        print("Disconnected, stop sending data")
        self.stop_bluetooth_read_write()
        self.robi.motors.disable()

    async def _await_start_confirmation(self):
        await self.start_confirmation_characteristic.written()

    @staticmethod
    def calculate_motor_speeds(v: float, s: float) -> tuple[float]:
        """
        Convert velocity (0-1) and steering (0-1) into left and right motor speeds.
        
        :param v: Velocity (0 to 1)
        :param s: Steering (0 = full left, 1 = full right, 0.5 = straight)
        :return: (left_motor_speed, right_motor_speed)
        """
        # Convert steering range (0-1) to (-1 to 1), where -1 is full left, 1 is full right
        steering_offset = (s - 0.5) * 2
        
        # Calculate motor speeds
        left_speed = v * (1 + steering_offset)  # Reduce left speed when steering right
        right_speed = v * (1 - steering_offset)  # Reduce right speed when steering left
        
        # Clip values to ensure they stay within 0-1
        left_speed = max(0, min(1, left_speed))
        right_speed = max(0, min(1, right_speed))

        return left_speed, right_speed

    def _update_motors_to_velocity_and_steering(self):


        left_speed, right_speed = self.calculate_motor_speeds(self._current_velocity_value, self._current_steering_value)


        left_freq = int(left_speed * self.maximum_motor_frequency)
        right_freq = int(right_speed * self.maximum_motor_frequency)


        #print("Calculated motor speeds", left_speed, right_speed)

        #print("Received velocity and steering data", self._current_velocity_value, self._current_steering_value)

        #print("Calculated motor frequencies", left_freq, right_freq)

        if left_freq < 100:
            self.robi.motors.left.disable()
        else:
            self.robi.motors.left.enable()
            self.robi.motors.left.set_freq(left_freq)

        if right_freq < 100:
            self.robi.motors.right.disable()
        else:
            self.robi.motors.right.enable()
            self.robi.motors.right.set_freq(right_freq)

    async def _remote_control_velocity_task(self):
        while self._read_remote_control:
            await self.velocity_characteristic.written()
            vel_bytes = self.velocity_characteristic.read()
            self._current_velocity_value = int.from_bytes(vel_bytes, "big") / 255
            self._update_motors_to_velocity_and_steering()

    async def _remote_control_steering_task(self):
        while self._read_remote_control:
            await self.steering_characteristic.written()
            steering_bytes = self.steering_characteristic.read()
            self._current_steering_value = int.from_bytes(steering_bytes, "big") / 255
            self._update_motors_to_velocity_and_steering()

    async def _start_remote_control_tasks(self):
        tasks = [
            asyncio.create_task(self._remote_control_velocity_task()),
            asyncio.create_task(self._remote_control_steering_task()),
        ]
        await asyncio.gather(*tasks)

    async def _rsrc_update_task(self):
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
        while self._send_rsrc_data:
            sampled_state = self.robi.sample_state(frame_id)

            self.ble.write_data_to_characteristic(
                self.rsrc_characteristic, sampled_state.as_bytes()
            )

            # TODO: Sample and send data in background

            await asyncio.sleep(self.state_update_delay_ms / 1000)

            frame_id += 1

    async def _run(self):

        while self._advertise:

            print("Waiting for connection")

            connection = await self.ble.advertise_and_wait_for_connection()

            print("Connected")

            tasks = [
                asyncio.create_task(self._wait_for_disconnection(connection)),
                asyncio.create_task(self._start_remote_control_tasks()),
                asyncio.create_task(self._rsrc_update_task())
            ]

            await asyncio.gather(*tasks)

    @property
    def is_seding_or_receiving(self):
        return self._send_rsrc_data or self._read_remote_control

    @property
    def is_running(self):
        return self._send_rsrc_data or self._advertise or self._read_remote_control


async def main():

    FWD = False

    robi = Robi42()
    robi.motors.set_direction(FWD)
    robi_live = RobiLive(robi)
    robi_live.start()

    while robi_live.is_running:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
