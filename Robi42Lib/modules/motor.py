from time import sleep_ms

from machine import Pin, PWM

from ..abstract import piopwm

from . import base_module


class _Motor:
    __current_freq: int

    def __init__(
        self,
        pin_en: base_module.DigitalBoardPin,
        pin_m0: base_module.DigitalBoardPin,
        pin_m1: base_module.DigitalBoardPin,
        pin_m2: base_module.DigitalBoardPin,
        pin_dir: base_module.DigitalBoardPin,
        step_pwm: piopwm.PIOPWM | PWM,
    ):
        self.__pin_en = pin_en
        self.__pin_m0 = pin_m0
        self.__pin_m1 = pin_m1
        self.__pin_m2 = pin_m2
        self.__pin_dir = pin_dir
        self._step_pwm = step_pwm

        self.disable()
        self.set_freq(420)
        self.set_stepping_size(True, True, True)
        self.set_direction(Motors.DIR_FORWARD)

    def enable(self):
        self.__pin_en.off()

    def disable(self):
        self.__pin_en.on()

    def set_freq(self, freq: int):
        self.__current_freq = freq
        self._step_pwm.freq(freq)

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        """
        |m0|m1|m2|Step Mode|
        |---|---|---|---|
        |0|0|0|Full step (2-phase excitation) with 71% current|
        |1|0|0|1/2 step (1-2 phase excitation)|
        |0|1|0|1/4 step (W1-2 phase excitation)|
        |1|1|0|8 microsteps/step|
        |0|0|1|16 microsteps/step|
        |1|0|1|32 microsteps/step|
        |0|1|1|32 microsteps/step|
        |1|1|1|32 microsteps/step|
        """
        self.__pin_m0.value(m0)
        self.__pin_m1.value(m1)
        self.__pin_m2.value(m2)

    def set_direction(self, direction: bool):
        ...

    def lock(self):
        ...

    def unlock(self):
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

    def accelerate(
        self,
        a: float,
        from_v: float,
        to_v: float,
        s_limit: float = 1000,
        wheel_radius: float = 0.032,
    ):
        """
        @param a: Acceleration in m/s^2
        @param from_v: Initial velocity in m/s
        @param to_v: Target velocity in m/s
        @param s_limit: Maximum distance to drive in m
        @param wheel_radius: Wheel radius in m
        @return: Reached velocity in m/s, distance covered in m
        """
        v = from_v  # m/s
        s = 0  # m
        dt = 0.0011  # s, TODO: Find a way to calibrate this value

        if a < 0:
            while v > to_v and s < s_limit:
                self.set_velocity(v, wheel_radius)
                v += dt * a
                s += dt * v
        else:
            while v < to_v and s < s_limit:
                self.set_velocity(v, wheel_radius)
                v += dt * a
                s += dt * v

        return v, s

    def set_velocity(self, v: float, wheel_radius: float = 0.032):
        # Dieser magische ↓ Wert ergibt sich aus 1.8 / 32 * (math.pi / 180) :)
        f = int(v / (0.00098174 * wheel_radius))

        if f <= 7:
            self.disable()
            return
        self.enable()
        self.set_freq(f)


class _MotorLeft(_Motor):

    def __init__(self):
        super().__init__(
            pin_en=base_module.DigitalBoardPin(base_module.DigitalBoardPins.ml_en),
            pin_m0=base_module.DigitalBoardPin(base_module.DigitalBoardPins.ml_m0),
            pin_m1=base_module.DigitalBoardPin(base_module.DigitalBoardPins.ml_m1),
            pin_m2=base_module.DigitalBoardPin(base_module.DigitalBoardPins.ml_m2),
            pin_dir=base_module.DigitalBoardPin(base_module.DigitalBoardPins.ml_dir),
            step_pwm=piopwm.PIOPWM(20, 420),
        )

    def set_direction(self, direction: bool):
        self.__pin_dir.value(direction)

    def lock(self):
        self.enable()
        self.set_freq(8)  # TODO: Find better way to lock motor

    def unlock(self):
        self.set_freq(420)
        self.disable()


class _MotorRight(_Motor):

    def __init__(self) -> None:
        step_pwm = PWM(Pin(21, Pin.OUT))
        step_pwm.duty_u16(32768)
        super().__init__(
            pin_en=base_module.DigitalBoardPin(base_module.DigitalBoardPins.mr_en),
            pin_m0=base_module.DigitalBoardPin(base_module.DigitalBoardPins.mr_m0),
            pin_m1=base_module.DigitalBoardPin(base_module.DigitalBoardPins.mr_m1),
            pin_m2=base_module.DigitalBoardPin(base_module.DigitalBoardPins.mr_m2),
            pin_dir=base_module.DigitalBoardPin(base_module.DigitalBoardPins.mr_dir),
            step_pwm=step_pwm,
        )

    def set_direction(self, direction: bool):
        self.__pin_dir.value(not direction)

    def set_duty_u16(self, duty_cycle: int):
        self._step_pwm.duty_u16(duty_cycle)

    def lock(self):
        self.enable()
        self.set_duty_u16(0)

    def unlock(self):
        self.set_duty_u16(32768)
        self.disable()


class Motors(base_module.BaseModule):
    DIR_FORWARD = True
    DIR_BACKWARD = False

    def __init__(self) -> None:
        self.left = _MotorLeft()
        self.right = _MotorRight()

    def disable(self):
        self.left.disable()
        self.right.disable()

    def enable(self):
        self.left.enable()
        self.right.enable()

    def set_freq(self, freq: int):
        self.left.set_freq(freq)
        self.right.set_freq(freq)

    def lock(self):
        self.left.lock()
        self.right.lock()

    def unlock(self):
        self.left.unlock()
        self.right.unlock()

    def set_stepping_size(self, m0: bool, m1: bool, m2: bool):
        """
        |m0|m1|m2|Step Mode|
        |---|---|---|---|
        |0|0|0|Full step (2-phase excitation) with 71% current|
        |1|0|0|1/2 step (1-2 phase excitation)|
        |0|1|0|1/4 step (W1-2 phase excitation)|
        |1|1|0|8 microsteps/step|
        |0|0|1|16 microsteps/step|
        |1|0|1|32 microsteps/step|
        |0|1|1|32 microsteps/step|
        |1|1|1|32 microsteps/step|
        """
        self.left.set_stepping_size(m0, m1, m2)
        self.right.set_stepping_size(m0, m1, m2)

    def set_direction(self, direction: bool):
        self.left.set_direction(direction)
        self.right.set_direction(direction)

    def accelerate(
        self,
        a: float,
        from_v: float,
        to_v: float,
        s_limit: float = 1000,
        wheel_radius: float = 0.032,
    ):
        """
        @param a: Acceleration in m/s^2
        @param from_v: Initial velocity in m/s
        @param to_v: Target velocity in m/s
        @param s_limit: Maximum distance to drive in m
        @param wheel_radius: Wheel radius in m
        @return: Reached velocity in m/s, distance covered in m
        """
        v = from_v  # m/s
        s = 0  # m
        dt = 0.0011  # s, TODO: Find a way to calibrate this value

        if a < 0:
            while v > to_v and s < s_limit:
                self.set_velocity(v, wheel_radius)
                v += dt * a
                s += dt * v
        else:
            while v < to_v and s < s_limit:
                self.set_velocity(v, wheel_radius)
                v += dt * a
                s += dt * v

        return v, s

    def set_velocity(self, v: float, wheel_radius: float = 0.032):
        # Dieser magische ↓ Wert ergibt sich aus 1.8 / 32 * (math.pi / 180) :)
        f = int(v / (0.00098174 * wheel_radius))

        if f <= 7:
            self.disable()
            return
        self.enable()
        self.set_freq(f)
