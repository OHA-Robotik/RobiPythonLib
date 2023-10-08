from . import base_module


class Buttons(base_module.BaseModule):

    def __init__(self) -> None:
        self.up = base_module.DigitalBoardPin(
            base_module.DigitalBoardPins.btn_up,
            mode=base_module.DigitalBoardPin.IN,
            pull=base_module.DigitalBoardPin.PULL_UP,
        )
        self.down = base_module.DigitalBoardPin(
            base_module.DigitalBoardPins.btn_down,
            mode=base_module.DigitalBoardPin.IN,
            pull=base_module.DigitalBoardPin.PULL_UP,
        )
        self.center = base_module.DigitalBoardPin(
            base_module.DigitalBoardPins.btn_center,
            mode=base_module.DigitalBoardPin.IN,
            pull=base_module.DigitalBoardPin.PULL_UP,
        )
        self.left = base_module.DigitalBoardPin(
            base_module.DigitalBoardPins.btn_left,
            mode=base_module.DigitalBoardPin.IN,
            pull=base_module.DigitalBoardPin.PULL_UP,
        )
        self.right = base_module.DigitalBoardPin(
            base_module.DigitalBoardPins.btn_right,
            mode=base_module.DigitalBoardPin.IN,
            pull=base_module.DigitalBoardPin.PULL_UP,
        )
