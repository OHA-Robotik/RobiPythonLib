from Robi42Lib.mcps import motor_and_taster_mcp
from machine import Pin, PWM


class Motor:
    def __init__(self, is_left_motor: bool) -> None:
        self.step_pwm = PWM(Pin(21 - is_left_motor, Pin.OUT))
        self.step_pwm.freq(0)
        self.step_pwm.duty_u16(32000)
        self.disable()

    def enable(self):
        raise NotImplementedError()
        motor_and_taster_mcp.digitalWrite(15, 0)

    def disable(self):
        raise NotImplementedError()
        motor_and_taster_mcp.digitalWrite(15, 1)

    def set_freq(self, freq: int):
        self.step_pwm.freq(freq)


class MotorLeft(Motor):
    def __init__(self) -> None:
        super().__init__(1)


class MotorRight(Motor):
    def __init__(self) -> None:
        super().__init__(0)
