from . import base_module


class Buttons(base_module.BaseModule):

    conf = {
        'up': 11,
        'down': 12,
        'center': 8,
        'left': 9,
        'right': 10,
    }

    def __init__(self) -> None:
        self.up = base_module.DigitalBoardPin('button_up')
        self.down = base_module.DigitalBoardPin('button_down')
        self.center = base_module.DigitalBoardPin('button_center')
        self.left = base_module.DigitalBoardPin('button_left')
        self.right = base_module.DigitalBoardPin('button_right')
