from Robi42Lib.AdminMenu.admin_menu import SubmenuList, Menu
from Robi42Lib.robi42 import Robi42
from time import sleep


class HardwareTestMenu(SubmenuList):
    def __init__(self, robi: Robi42, origin: Menu):
        super().__init__("HW Test", robi, origin, [LedTestMenu(robi, self)])


class LedTestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | None):
        super().__init__("Led Test", "Testing Leds...", robi, origin)

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
