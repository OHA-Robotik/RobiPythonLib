import time

from Robi42Lib.robi42 import Robi42


class LineMapper:

    def __init__(self, robi: Robi42, resolution: float = 0.005):
        self.robi = robi
        self.resolution = resolution
        self.run = False

    def start(self, time_limit: float):

        self.run = True
        threshold = 200

        with open("ir_read.txt", "w") as f:
            f.write(f"{self.resolution}\n")

        self.robi.motors.enable()

        time_passed = 0

        with open("ir_read.txt", "a") as f:
            while self.run and time_passed < time_limit:
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

                freq_left = self.robi.motors.left.freq
                freq_right = self.robi.motors.right.freq
                line = f"{freq_left} {freq_right} : {raw_l}, {raw_m}, {raw_r}\n"
                f.write(line)

                time.sleep(self.resolution)
                time_passed += self.resolution

        self.robi.motors.disable()

    def stop(self):
        self.run = False


def main():

    r = Robi42()
    lm = LineMapper(r, 0.05)
    lm.start(50)


if __name__ == "__main__":
    main()
