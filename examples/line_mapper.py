import time

from Robi42Lib.robi42 import Robi42
from machine import Timer

FWD = True
BWD = not FWD


def encode_data(
    freq_left: int,
    freq_right: int,
    left_direction: bool,
    right_direction: bool,
    raw_l: int,
    raw_m: int,
    raw_r: int,
) -> bytes:
    return (
        freq_left.to_bytes(2, "big")
        + freq_right.to_bytes(2, "big")
        + (
            (int(left_direction == FWD) << 31)
            | (int(right_direction == FWD) << 30)
            | raw_l << 20
            | raw_m << 10
            | raw_r
        ).to_bytes(4, "big")
    )


class LineMapper:
    def __init__(self, robi: Robi42, resolution: float = 0.1):
        self.robi = robi
        self.resolution = resolution
        self.is_running = False
        self.threshold = 200

    def _timer_callback(self, timer: Timer):
        freq_left = self.robi.motors.left.freq
        freq_right = self.robi.motors.right.freq
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()

        data = encode_data(
            freq_left,
            freq_right,
            self.robi.motors.left.direction,
            self.robi.motors.right.direction,
            raw_l,
            raw_m,
            raw_r,
        )

        try:
            self.f.write(data)
        except OSError:
            self.robi.lcd.turn_on()
            self.robi.lcd.put_str("D:")
            self.is_running = False

    def step(self, timer: Timer):
        threshold = 200
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()

        l_dark = raw_l < threshold
        m_dark = raw_m < threshold
        r_dark = raw_r < threshold

        if m_dark:
            if not l_dark and not r_dark:
                self.robi.motors.left.set_freq(5000)
                self.robi.motors.right.set_freq(5000)
            elif l_dark and not r_dark:
                self.robi.motors.left.set_freq(2000)
                self.robi.motors.right.set_freq(4000)
            elif r_dark and not l_dark:
                self.robi.motors.left.set_freq(4000)
                self.robi.motors.right.set_freq(2000)
        else:
            if l_dark and not r_dark:
                self.robi.motors.left.set_freq(300)
                self.robi.motors.right.set_freq(4000)
            elif r_dark and not l_dark:
                self.robi.motors.left.set_freq(4000)
                self.robi.motors.right.set_freq(300)

    def start(self):

        with open("ir_read.bin", "wb") as f:
            resolution_byte = int(self.resolution * 1000).to_bytes(2, "big")
            f.write(resolution_byte)

        self.f = open("ir_read.bin", "ab")

        timer = Timer(-1)
        step_timer = Timer(-1)
        tick = int(self.resolution * 1000)
        self.is_running = True

        self.robi.motors.enable()

        step_timer.init(period=tick, callback=self.step)
        timer.init(period=tick, callback=self._timer_callback)

        while self.is_running:
            if not self.robi.buttons.center.value():
                self.is_running = False
                break
            time.sleep(0.1)

        step_timer.deinit()
        timer.deinit()
        self.robi.motors.disable()
        self.f.close()


def main():
    r = Robi42()
    lm = LineMapper(r)
    lm.start()


if __name__ == "__main__":
    main()
