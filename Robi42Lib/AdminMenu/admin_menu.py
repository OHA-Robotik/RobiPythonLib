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
                while robi.buttons.left.is_pressed():
                    sleep(0.1)
                return ButtonInput.left
            if robi.buttons.right.is_pressed():
                while robi.buttons.right.is_pressed():
                    sleep(0.1)
                return ButtonInput.right
            if robi.buttons.center.is_pressed():
                while robi.buttons.center.is_pressed():
                    sleep(0.1)
                return ButtonInput.center
            if robi.buttons.up.is_pressed():
                while robi.buttons.up.is_pressed():
                    sleep(0.1)
                return ButtonInput.up
            if robi.buttons.down.is_pressed():
                while robi.buttons.down.is_pressed():
                    sleep(0.1)
                return ButtonInput.down
            sleep(0.1)


class Menu:

    header: str
    content: str

    def __init__(self, header: str, content: str, robi: Robi42, origin: "Menu"):
        self.header = header
        self.content = content
        self.robi = robi
        self.origin = origin

    def goto(self):
        self.robi.lcd.clear()
        self.robi.lcd.putstr(self.content)
        self.main_loop()

    def main_loop(self):
        raise NotImplementedError()


class SubmenuList:
    selection = 0

    def __init__(
        self,
        header: str,
        robi: Robi42,
        origin: Menu,
        submenus: list[Menu | "SubmenuList"],
    ):
        self.header = header
        self.robi = robi
        self.origin = origin
        self.submenus = submenus
        self.max_idx = len(submenus) - 1
        self.submenu_headers = [s.header for s in submenus]

    def goto(self):
        self.robi.lcd.clear()
        self.show_cursor()
        self.scroll_to_selection()
        self.main_loop()

    def show_cursor(self):
        self.robi.lcd.show_cursor()
        self.robi.lcd.blink_cursor_on()

    def hide_cursor(self):
        self.robi.lcd.hide_cursor()
        self.robi.lcd.blink_cursor_off()

    def main_loop(self):
        while True:

            self.highlight_selection()

            inp = ButtonInput.wait_for_input(self.robi)

            if inp == ButtonInput.down:
                self.selection += 1
                self.correct_selection()
                self.scroll_to_selection()
            elif inp == ButtonInput.up:
                self.selection -= 1
                self.correct_selection()
                self.scroll_to_selection()
            elif inp == ButtonInput.center:
                self.hide_cursor()
                self.submenus[self.selection].goto()
                self.scroll_to_selection()
            elif inp == ButtonInput.left and self.origin is not None:
                break

        self.hide_cursor()

    def correct_selection(self):
        if self.selection < 0:
            self.selection = self.max_idx
        elif self.selection > self.max_idx:
            self.selection = 0

    def scroll_to_selection(self):
        self.robi.lcd.clear()

        if self.selection % 2 == 1:
            self.robi.lcd.putstr(self.submenu_headers[self.selection - 1])
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.putstr(self.submenu_headers[self.selection])
            return

        self.robi.lcd.putstr(self.submenu_headers[self.selection])
        if self.selection < self.max_idx:
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.putstr(self.submenu_headers[self.selection + 1])

    def highlight_selection(self):
        self.robi.lcd.move_to(15, self.selection & 1)


class TestMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu):
        super().__init__("Test Menu", "This is a test menu", robi, origin)

    def main_loop(self):
        while ButtonInput.wait_for_input(self.robi) != ButtonInput.left:
            pass


class MainMenu(SubmenuList):
    def __init__(self, robi: Robi42):
        from Robi42Lib.AdminMenu.hardware_test import HardwareTestMenu
        from Robi42Lib.AdminMenu.i2c_scanner import HardwareScannerMenu

        super().__init__(
            "Main Menu",
            robi,
            None,
            [HardwareTestMenu(robi, self), HardwareScannerMenu(robi, self)],
        )
        robi.lcd.on()


if __name__ == "__main__":
    with Robi42(
        enable_gyro=False,
        enable_ir_sensors=False,
        enable_laser_sensor=False,
        enable_motors=False,
    ) as r:
        MainMenu(r).goto()
