from Robi42Lib.mcps import motor_and_button_mcp
from machine import Pin, PWM


class MotorLeft:
    def __init__(self) -> None:
        self.disable()
        self.step_pwm = PWM(Pin(20, Pin.OUT))
        self.step_pwm.freq(420)
        self.step_pwm.duty_u16(32768)
        self.set_stepping_size(1, 1, 1)
        self.set_direction(1)

    def enable(self):
        motor_and_button_mcp.digital_write(14, 0)

    def disable(self):
        motor_and_button_mcp.digital_write(14, 1)

    def set_freq(self, freq: int):
        self.step_pwm.freq(freq)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        m0, m1, m2 = bool(m0), bool(m1), bool(m2)
        motor_and_button_mcp.digital_write(0, m0)
        motor_and_button_mcp.digital_write(1, m1)
        motor_and_button_mcp.digital_write(2, m2)

    def set_direction(self, direction: bool):
        direction = bool(direction)
        motor_and_button_mcp.digital_write(3, direction)


class MotorRight:
    def __init__(self) -> None:
        self.disable()
        self.step_pwm = PWM(Pin(21, Pin.OUT))
        self.step_pwm.freq(420)
        self.step_pwm.duty_u16(32768)
        self.set_stepping_size(1, 1, 1)
        self.set_direction(0)

    def enable(self):
        motor_and_button_mcp.digital_write(15, 0)

    def disable(self):
        motor_and_button_mcp.digital_write(15, 1)

    def set_freq(self, freq: int):
        self.step_pwm.freq(freq)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        m0, m1, m2 = bool(m0), bool(m1), bool(m2)
        motor_and_button_mcp.digital_write(4, m0)
        motor_and_button_mcp.digital_write(5, m1)
        motor_and_button_mcp.digital_write(6, m2)

    def set_direction(self, direction: bool):
        direction = bool(direction)
        motor_and_button_mcp.digital_write(7, not direction)


class Motors:

    dir_forward = True
    dir_backward = False

    def __init__(self) -> None:
        self.left = MotorLeft()
        self.right = MotorRight()

    def disable(self):
        self.left.disable()
        self.right.disable()

    def enable(self):
        self.left.enable()
        self.right.enable()

    def set_freq(self, freq: int):
        self.left.set_freq(freq)
        self.right.set_freq(freq)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        self.left.set_stepping_size(m0, m1, m2)
        self.right.set_stepping_size(m0, m1, m2)

    def set_direction(self, direction: bool):
        self.left.set_direction(direction)
        self.right.set_direction(direction)
