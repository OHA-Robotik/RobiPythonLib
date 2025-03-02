from .... import robi42
from . import abstract
from .. import utils

"""

The state of all buttons is represented by an 8-bit value:

| Bit Position | Represented Button |
|--------------|--------------------|
| 0 (MSB)      | Center Button      |
| 1            | Left Button        |
| 2            | Right Button       |
| 3            | Top Button         |
| 4            | Bottom Button      |
| 5            | (Unused)           |
| 6            | (Unused)           |
| 7 (LSB)      | (Unused)           |
"""


class ButtonsFrameData(abstract.AbstractFrameData):

    def __init__(
        self,
        *,
        left_button_is_pressed: bool,
        right_button_is_pressed: bool,
        center_button_is_pressed: bool,
        up_button_is_pressed: bool,
        down_button_is_pressed: bool
    ):
        self.buttons_byte = utils.to_bytes(
            center_button_is_pressed << 7
            | left_button_is_pressed << 6
            | right_button_is_pressed << 5
            | up_button_is_pressed << 4
            | down_button_is_pressed << 3,
            0xFF,
        )

    @property
    def bytes(self) -> bytes:
        return self.buttons_byte

    @staticmethod
    def sample(robi: robi42.Robi42) -> "ButtonsFrameData":
        return ButtonsFrameData(
            left_button_is_pressed=robi.buttons.left.value() == 0,
            right_button_is_pressed=robi.buttons.right.value() == 0,
            center_button_is_pressed=robi.buttons.center.value() == 0,
            up_button_is_pressed=robi.buttons.up.value() == 0,
            down_button_is_pressed=robi.buttons.down.value() == 0,
       )
