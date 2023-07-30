from . import base_module


class Buttons(base_module.BaseModule):

    def __init__(self) -> None:
        self.up = base_module.DigitalBoardPin(base_module.DigitalBoardPins.btn_up)
        self.down = base_module.DigitalBoardPin(base_module.DigitalBoardPins.btn_down)
        self.center = base_module.DigitalBoardPin(base_module.DigitalBoardPins.btn_center)
        self.left = base_module.DigitalBoardPin(base_module.DigitalBoardPins.btn_left)
        self.right = base_module.DigitalBoardPin(base_module.DigitalBoardPins.btn_right)
