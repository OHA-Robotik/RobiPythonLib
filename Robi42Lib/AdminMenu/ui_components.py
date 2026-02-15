from time import sleep, ticks_ms
from ..robi42 import Robi42
from ..modules.buttons import Button


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

    @staticmethod
    def wait_for_release(button: Button):
        while button.is_pressed():
            sleep(0.01)

    @staticmethod
    def wait_for_button_press(button: Button):
        while not button.is_pressed():
            sleep(0.01)


class Menu:
    header: str
    content: str

    def __init__(self, header: str, content: str, robi: Robi42, origin: "Menu", refresh_rate: int = 10):
        self.header = header
        self.content = content
        self.robi = robi
        self.origin = origin
        self.refresh_delay_ms = 1 / refresh_rate * 1000

    def goto(self):
        self.robi.lcd.clear()
        self.robi.lcd.put_str(self.content)

        self.begin()

        ex = False

        while not ex:

            self.main_loop()
            s = ticks_ms()

            ex = self.robi.buttons.left.is_pressed()
            while ticks_ms() - s < self.refresh_delay_ms and not ex:
                ex = self.robi.buttons.left.is_pressed()

        ButtonInput.wait_for_release(self.robi.buttons.left)

        self.exit()

    def begin(self):
        ...

    def main_loop(self):
        raise NotImplementedError()

    def exit(self):
        ...


class SubmenuList:
    selection = 0

    def __init__(
            self,
            header: str,
            robi: Robi42,
            origin: Menu | None,
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
            self.robi.lcd.put_str(self.submenu_headers[self.selection - 1])
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.put_str(self.submenu_headers[self.selection])
            return

        self.robi.lcd.put_str(self.submenu_headers[self.selection])
        if self.selection < self.max_idx:
            self.robi.lcd.move_to(0, 1)
            self.robi.lcd.put_str(self.submenu_headers[self.selection + 1])

    def highlight_selection(self):
        self.robi.lcd.move_to(15, self.selection & 1)
