from Robi42Lib.robi42 import Robi42
from time import sleep


class ButtonInput:
    up = 0
    down = 1
    left = 2
    right = 3
    center = 4

    @staticmethod
    def wait_for_input(robi: Robi42) -> int:
        while True:
            if robi.buttons.left.is_pressed():
                return ButtonInput.left
            if robi.buttons.right.is_pressed():
                return ButtonInput.right
            if robi.buttons.center.is_pressed():
                return ButtonInput.center
            if robi.buttons.up.is_pressed():
                return ButtonInput.up
            if robi.buttons.down.is_pressed():
                return ButtonInput.down
            sleep(0.1)


class Menu:

    header: str

    def __init__(self, robi: Robi42, origin: "Menu" | None):
        self.robi = robi
        self.origin = origin

    def goto(self):
        raise NotImplementedError()

    def main_loop(self):
        raise NotImplementedError()


class SubmenuList:
    selection = 0

    def __init__(self, robi: Robi42, origin: Menu, submenus: list[Menu]):
        self.robi = robi
        self.origin = origin
        self.submenus = submenus
        self.max_idx = len(submenus) - 1
        self.submenu_headers = list(submenus.keys())

        robi.lcd.clear()

        if self.max_idx >= 0:
            robi.lcd.putstr(self.submenu_headers[0])

            if self.max_idx > 0:
                robi.lcd.putstr("\n" + self.submenu_headers[1])

    def goto(self):
        self.main_loop()

    def main_loop(self):
        while True:

            self.highlight_selection()

            inp = ButtonInput.wait_for_input(self.robi)

            if inp == ButtonInput.down:
                self.selection += 1
            elif inp == ButtonInput.up:
                self.selection -= 1

                if self.selection < 0:
                    self.selection = self.max_idx
                elif self.selection > self.max_idx:
                    self.selection = 0

            elif inp == ButtonInput.left:
                self.origin.goto()

    def highlight_selection(self):
        self.robi.lcd.show_cursor()
        self.robi.lcd.blink_cursor_on()
        self.robi.lcd.move_to(15, self.selection & 1)


class TestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu):
        super().__init__(robi, origin)
        self.header = "Test Menu"

    def goto(self):
        self.robi.lcd.clear()
        self.robi.lcd.putstr("This is the test menu")
        TestMenu.main_loop()

    def main_loop(self):
        while True:
            inp = ButtonInput.wait_for_input(self.robi)

            if inp == ButtonInput.left:
                self.origin.goto()

            sleep(0.1)


class MainMenu(Menu):
    submenus = [TestMenu, TestMenu]

    def __init__(self, robi: Robi42):
        super().__init__(robi, None)
        robi.lcd.on()

    def goto(self):
        self.robi.lcd.clear()
        self.robi.lcd.putstr("This is the main menu")
        MainMenu.main_loop()

    def main_loop(self):
        while True:
            inp = ButtonInput.wait_for_input(self.robi)

            if inp == ButtonInput.center:
                SubmenuList(self.robi, self.submenus, self).goto()

            sleep(0.1)


if __name__ == "__main__":
    r = Robi42(
        enable_gyro=False,
        enable_ir_sensors=False,
        enable_laser_sensor=False,
        enable_leds=False,
        enable_motors=False,
        enable_piezo=False,
        enable_poti=False,
    )
    MainMenu(r).goto()
