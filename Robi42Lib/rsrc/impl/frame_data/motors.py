from .... import robi42
from . import abstract
import struct


class MotorsFrameData(abstract.AbstractFrameData):

    MIN_ANGULAR_VELOCITY = -300
    MAX_ANGULAR_VELOCITY = 300
    SCALE_FACTOR = 100

    def __init__(
        self, *, left_motor_angular_velocity: float, right_motor_angular_velocity: float
    ):
        assert (
            self.MIN_ANGULAR_VELOCITY
            <= left_motor_angular_velocity
            <= self.MAX_ANGULAR_VELOCITY
        )
        assert (
            self.MIN_ANGULAR_VELOCITY
            <= right_motor_angular_velocity
            <= self.MAX_ANGULAR_VELOCITY
        )

        self.left_motor_angular_velocity_bytes = struct.pack(
            ">h", int(left_motor_angular_velocity * self.SCALE_FACTOR)
        )
        self.right_motor_angular_velocity_bytes = struct.pack(
            ">h", int(right_motor_angular_velocity * self.SCALE_FACTOR)
        )

    @property
    def bytes(self) -> bytes:
        return (
            self.left_motor_angular_velocity_bytes
            + self.right_motor_angular_velocity_bytes
        )

    @staticmethod
    def sample(robi: robi42.Robi42) -> "MotorsFrameData":
        return MotorsFrameData(
            left_motor_angular_velocity=robi.motors.left.angular_velocity,
            right_motor_angular_velocity=robi.motors.right.angular_velocity,
        )
