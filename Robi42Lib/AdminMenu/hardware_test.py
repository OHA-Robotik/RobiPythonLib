from time import sleep

from .ui_components import SubmenuList, Menu
from ..modules.motor import _Motor, MotorSide
from ..modules.piezo import Tone
from ..robi42 import Robi42


class HardwareTestMenu(SubmenuList):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList):
        # TODO: only init the menus for connected components

        super().__init__(
            "HW Test",
            robi,
            origin,
            [
                LedTestMenu(robi, self),
                PotiTestMenu(robi, self),
                PiezoTestMenu(robi, self),
                MotorsTestMenu(robi, self),
                LaserSensorTestMenu(robi, self),
                IrSensorsTestMenu(robi, self),
            ],
        )


class LedTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("LEDs Test", "", robi, origin, refresh_rate=2)
        self.on = True

    def begin(self):
        self.on = True

    def main_loop(self):
        self.robi.lcd.clear()
        if self.on:
            self.robi.leds.all.on()
            self.robi.lcd.put_str("Leds ON")
        else:
            self.robi.leds.all.off()
            self.robi.lcd.put_str("Leds OFF")
        self.on = not self.on

    def exit(self):
        self.robi.leds.all.off()


class PotiTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Poti Test", "", robi, origin)
        self.old_raw_val = -1
        self.old_val = -1

    def begin(self):
        self.old_raw_val = -1
        self.old_val = -1

    def main_loop(self):
        raw = self.robi.poti.get_raw_value()
        value = self.robi.poti.get_value()

        if raw != self.old_raw_val:
            self.robi.lcd.move_to(0, 0)
            self.robi.lcd.put_str(f"Raw: {raw}    ")
        if value != self.old_val:
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.put_str(f"Value: {value:.05f}")

class PiezoTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Piezo Test", "", robi, origin, 2)
        self.freq = 100
        self.tone_length_ms = int(self.refresh_delay_ms)

    def begin(self):
        self.freq = 100
        self.robi.lcd.put_str("Frequenz:")

    def main_loop(self):
        if self.freq > 8000:
            self.freq = 100

        self.robi.lcd.move_to(0, 1)
        self.robi.lcd.put_str(f"{self.freq} Hz    ")
        self.robi.piezo.play_tone(Tone("", self.freq, self.tone_length_ms))
        self.freq += 200


class MotorsTestMenu(SubmenuList):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList):
        super().__init__(
            "Motor Test",
            robi,
            origin,
            [
                MotorTestMenu(robi, self, robi.motors.left),
                MotorTestMenu(robi, self, robi.motors.right),
            ],
        )

class MotorTestMenu(Menu):
    def __init__(
            self, robi: Robi42, origin: Menu | SubmenuList | None, motor: _Motor
    ):
        super().__init__(
            f"{'Linker' if motor.side == MotorSide.LEFT else 'Rechter'} Motor",
            "",
            robi,
            origin,
            5
        )
        self.motor = motor
        self.old_freq = 100

    def begin(self):
        for i in range(3, 0, -1):
            self.robi.lcd.clear()
            self.robi.lcd.put_str(f"Motor started in {i}")
            sleep(1)

        self.robi.lcd.clear()
        self.robi.lcd.put_str("Freq (poti):")

        self.motor.enable()
        self.old_freq = 100

    def main_loop(self):
        freq = int(self.robi.poti.get_raw_value() / 1023 * 10_000)

        if abs(self.old_freq - freq) < 200:
            freq = self.old_freq

        if freq < 100 or freq > 10e3:
            freq = 100

        self.robi.motors.set_freq(freq) # for some reason self.motor.set_freq doesnt work
        
        self.robi.lcd.move_to(0, 1)
        self.robi.lcd.put_str(f"{self.motor.freq:,} Hz   ")
        self.old_freq = freq


    def exit(self):
        self.motor.disable()


class LaserSensorTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Laser Test", "", robi, origin)

    def begin(self):
        self.robi.lcd.put_str("Distance:")

    def main_loop(self):
        self.robi.lcd.move_to(0, 1)
        self.robi.lcd.put_str(f"{self.robi.laser_sensor.read_distance_mm():,} mm    ")

class IrSensorsTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Ir Sensor Test", "", robi, origin)

    def begin(self):
        self.robi.lcd.put_str("L       M      R")

    def main_loop(self):
        raw_l, raw_m, raw_r = self.robi.ir_sensors.read_raw_values()
        self.robi.lcd.move_to(0, 1)
        self.robi.lcd.put_str(f"{raw_l:<4}  {raw_m:^4}  {raw_r:>4}")
