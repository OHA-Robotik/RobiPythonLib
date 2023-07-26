from time import sleep_ms

from machine import Pin, PWM

from Robi42Lib.mcps import motor_and_button_mcp
from Robi42Lib.piopwm import PIOPWM


class Motor:
    __current_freq: int

    def __init__(self, pin: int, step_pwm: PIOPWM | PWM):
        self.__pin = pin
        self._step_pwm = step_pwm

        self.disable()
        self.set_freq(420)
        self.set_stepping_size(True, True, True)
        self.set_direction(True)

    def enable(self):
        motor_and_button_mcp.digital_write(self.__pin, 0)

    def disable(self):
        motor_and_button_mcp.digital_write(self.__pin, 1)

    def set_freq(self, freq: int):
        self.__current_freq = freq
        self._step_pwm.freq(freq)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        ...

    def set_direction(self, direction: bool):
        ...

    def accelerate_to_freq(self, freq: int, hz_per_second: int):
        freq_dif = freq - self.freq
        delay_ms = 100
        step_size = int(hz_per_second * (delay_ms / 1000))

        if freq_dif > 0:
            for f in range(self.freq + step_size, freq, step_size):
                self.set_freq(f)
                sleep_ms(delay_ms)
            self.set_freq(freq)
        elif freq_dif < 0:
            for f in range(freq, self.freq, step_size)[::-1]:
                self.set_freq(f)
                sleep_ms(delay_ms)

    @property
    def freq(self):
        return self.__current_freq


class MotorLeft(Motor):

    def __init__(self):
        super().__init__(14, PIOPWM(20, 420))

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        motor_and_button_mcp.digital_write(0, m0)
        motor_and_button_mcp.digital_write(1, m1)
        motor_and_button_mcp.digital_write(2, m2)

    def set_direction(self, direction: bool):
        motor_and_button_mcp.digital_write(3, direction)


class MotorRight(Motor):

    def __init__(self) -> None:
        super().__init__(15, PWM(Pin(21, Pin.OUT)))
        self._step_pwm.duty_u16(32768)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        motor_and_button_mcp.digital_write(4, m0)
        motor_and_button_mcp.digital_write(5, m1)
        motor_and_button_mcp.digital_write(6, m2)

    def set_direction(self, direction: bool):
        motor_and_button_mcp.digital_write(7, not direction)


class Motors:
    DIR_FORWARD = True
    DIR_BACKWARD = False

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
