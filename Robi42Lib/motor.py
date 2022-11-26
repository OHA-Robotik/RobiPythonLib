from Robi42Lib.mcps import motor_and_taster_mcp
from machine import Pin, PWM

class MotorLeft:

    def __init__(self) -> None:
        self.step_pwm = PWM(Pin(21, Pin.OUT))
        self.step_pwm.freq(440)
        self.step_pwm.duty_u16(32000)

    def set_speed(self, speed: int):
        self.step_pwm.duty_u16(speed)