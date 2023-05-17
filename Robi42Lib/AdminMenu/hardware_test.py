from Robi42Lib.AdminMenu.admin_menu import SubmenuList, Menu
from Robi42Lib.robi42 import Robi42
from Robi42Lib.piezo import Tone
from Robi42Lib.motor import MotorLeft, MotorRight
from time import sleep


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
        super().__init__("Led Test", "", robi, origin)

    def main_loop(self):
        on = True
        while not self.robi.buttons.left.is_pressed():
            self.robi.lcd.clear()
            if on:
                self.robi.leds.on()
                self.robi.lcd.putstr("Leds ON")
            else:
                self.robi.leds.off()
                self.robi.lcd.putstr("Leds OFF")
            on = not on
            sleep(0.5)
        self.robi.leds.off()


class PotiTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Poti Test", "", robi, origin)

    def main_loop(self):
        while not self.robi.buttons.left.is_pressed():
            raw = self.robi.poti.get_raw_value()
            value = self.robi.poti.get_value()
            self.robi.lcd.clear()
            self.robi.lcd.putstr(f"Raw: {raw}")
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.putstr(f"Value: {value:.05f}")
            sleep(0.2)


class PiezoTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Piezo Test", "", robi, origin)

    def main_loop(self):
        freq = 100
        while not self.robi.buttons.left.is_pressed():

            if freq > 8000:
                freq = 100

            self.robi.lcd.clear()
            self.robi.lcd.putstr(f"Frequency: {freq}Hz")
            self.robi.piezo.play_tone(Tone("", freq))
            freq += 200


class MotorsTestMenu(SubmenuList):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList):

        robi.init_motors()
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
        self, robi: Robi42, origin: Menu | SubmenuList | None, motor: MotorRight | MotorLeft
    ):
        super().__init__(
            f"{'Left' if isinstance(motor, MotorLeft) else 'Right'} Motor",
            "",
            robi,
            origin,
        )
        self.motor = motor

    def main_loop(self):

        for i in range(5, 0, -1):
            self.robi.lcd.clear()
            self.robi.lcd.putstr(f"Motor starts in {i}s (use poti)")
            sleep(1)

        self.motor.enable()

        old_freq = 0

        while not self.robi.buttons.left.is_pressed():

            sleep(0.2)

            freq = int(self.robi.poti.get_raw_value() / 1024 * 150_000)

            if freq <= 1000:
                freq = 1000

            if abs(old_freq - freq) < 2000:
                continue

            self.motor.set_freq(freq)
            self.robi.lcd.clear()
            self.robi.lcd.putstr("Freq (use poti):")
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.putstr(f"{freq:,}Hz")

            old_freq = freq

        self.motor.disable()


class LaserSensorTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Laser Test", "", robi, origin)

    def main_loop(self):

        self.robi.init_laser_sensor()

        while not self.robi.buttons.left.is_pressed():
            self.robi.lcd.clear()
            self.robi.lcd.putstr("Distance:")
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.putstr(f"{self.robi.laser_sensor.get_distance():,}mm")
            sleep(0.3)


class IrSensorsTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Ir Sensor Test", "", robi, origin)

    def main_loop(self):

        self.robi.init_ir_sensors()

        while not self.robi.buttons.left.is_pressed():
            raw_l, raw_m, raw_r = self.robi.ir_sensors.get_raw_values()
            self.robi.lcd.clear()
            self.robi.lcd.putstr(f"Raw: L:{raw_l} M:{raw_m} R:{raw_r}")
            sleep(0.3)
