# Example of using PIO for PWM, and fading the brightness of an LED

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock).side(0)
    mov(x, osr)  # Keep most recent pull data stashed in X, for recycling by noblock

    mov(y, x)

    label("off_loop")
    jmp(y_dec, "off_loop")

    mov(y, x).side(1)

    label("on_loop")
    jmp(y_dec, "on_loop")


class PIOPWM:
    def __init__(self, pin: int, freq: int):
        self.count_freq = 100_000_000
        self._sm = StateMachine(0, pwm_prog, freq=self.count_freq, sideset_base=Pin(pin))
        self.freq(freq)
        self._sm.active(1)

    def _freq_to_max_count(self, freq: int):
        return self.count_freq // (freq * 2)

    def freq(self, freq: int):
        """Minimum value is -1 (completely turn off), 0 actually still produces narrow pulse"""
        assert freq >= -1
        self._sm.put(self._freq_to_max_count(freq))


if __name__ == "__main__":
    pwm = PIOPWM(20, 10_000)

    while True:
        sleep(1)
