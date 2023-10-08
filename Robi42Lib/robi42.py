from time import sleep as _sleep

from .modules import buttons as _mod_buttons
from .modules import piezo as _mod_piezo
from .modules import motor as _mod_motor
from .modules import poti as _mod_poti


class Robi42:

    def __init__(self,):
        self.buttons = _mod_buttons.Buttons()
        self.piezo = _mod_piezo.Piezo()
        self.motors = _mod_motor.Motors()
        self.poti = _mod_poti.Poti()
