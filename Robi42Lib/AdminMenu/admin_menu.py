from Robi42Lib.robi42 import Robi42
from time import sleep


with Robi42(
    enable_gyro=False,
    enable_ir_sensors=False,
    enable_laser_sensor=False,
    enable_leds=False,
    enable_motors=False,
    enable_piezo=False,
    enable_poti=False,
) as robi:

    class ButtonInput:
        up = 0
        down = 1
        left = 2
        right = 3
        center = 4

        @staticmethod
        def wait_for_input() -> int:
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
        pass

    class SubmenuList:
        selection = 0

        def __init__(self, submenus: dict[str:Menu]) -> None:
            assert len(submenus) > 0
            self.submenus = submenus
            self.max_idx = len(submenus) - 1
            self.submenu_headers = list(submenus.keys())

            robi.lcd.clear()

            if self.max_idx > 0:
                robi.lcd.putstr("\n" + self.submenu_headers[1])

            robi.lcd.putstr(self.submenu_headers[0])

        def main_loop(self):
            while True:
                inp = ButtonInput.wait_for_input()

                if inp == ButtonInput.down:
                    self.selection += 1
                elif inp == ButtonInput.up:
                    self.selection -= 1

                    if self.selection < 0:
                        self.selection = self.max_idx
                    elif self.selection > self.max_idx:
                        self.selection = 0

    class TestMenu(Menu):
        @staticmethod
        def goto():
            robi.lcd.clear()
            robi.lcd.putstr("This is the test menu")
            TestMenu.main_loop()

        @staticmethod
        def main_loop():
            while True:
                inp = ButtonInput.wait_for_input()

                if inp == ButtonInput.left:
                    MainMenu.goto()

                sleep(0.1)

    class MainMenu(Menu):
        submenus = {"test menu 1": TestMenu, "test menu 2": TestMenu}

        def __init__(self):
            robi.lcd.on()
            SubmenuList(self.submenus)

        @staticmethod
        def goto():
            robi.lcd.clear()
            robi.lcd.putstr("This is the main menu")
            MainMenu.main_loop()

        @staticmethod
        def main_loop():
            while True:
                inp = ButtonInput.wait_for_input()

                if inp == ButtonInput.center:
                    TestMenu.goto()

                sleep(0.1)


if __name__ == "__main__":
    MainMenu()
