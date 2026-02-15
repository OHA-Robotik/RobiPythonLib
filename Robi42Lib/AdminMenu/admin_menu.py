from .hardware_test import HardwareTestMenu
from .ui_components import Menu, SubmenuList, ButtonInput
from ..robi42 import Robi42


class MainMenu(SubmenuList):
    def __init__(self, robi: Robi42):

        super().__init__(
            "Hauptmenü",
            robi,
            None,
            [HardwareTestMenu(robi, self)],
        )
        robi.lcd.turn_on()


def start(robi: Robi42):
    MainMenu(robi).goto()
