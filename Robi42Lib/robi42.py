from time import sleep as _sleep

from .modules import buttons as _mod_buttons
from .modules import piezo as _mod_piezo


class Robi42:

    def __init__(self,):
        self.buttons = _mod_buttons.Buttons()
        self.piezo = _mod_piezo.Piezo()
