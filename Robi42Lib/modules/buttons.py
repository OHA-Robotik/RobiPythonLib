from . import base_module


class Button(base_module.DigitalBoardPin):

    def __init__(self, pin_id: str):
        super().__init__(pin_id, base_module.DigitalBoardPin.IN, base_module.DigitalBoardPin.PULL_UP)

    def is_pressed(self):
        return not self.value()


class Buttons(base_module.BaseModule):

    def __init__(self) -> None:
        self.up = Button(base_module.DigitalBoardPins.btn_up)
        self.down = Button(base_module.DigitalBoardPins.btn_down)
        self.center = Button(base_module.DigitalBoardPins.btn_center, )
        self.left = Button(base_module.DigitalBoardPins.btn_left, )
        self.right = Button(base_module.DigitalBoardPins.btn_right, )
