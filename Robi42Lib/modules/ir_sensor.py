from . import base_module


def convert(raw: int) -> float:
    if raw < 100:
        return 0
    if raw > 924:
        return 1
    return raw / 0b1111111111


class IrSensors(base_module.BaseModule):
    def __init__(self) -> None:
        self.left = base_module.AnalogBoardPin(base_module.AnalogBoardPins.ir_left)
        self.middle = base_module.AnalogBoardPin(base_module.AnalogBoardPins.ir_middle)
        self.right = base_module.AnalogBoardPin(base_module.AnalogBoardPins.ir_right)

    def read_raw_values(self) -> tuple[int, int, int]:
        return (
            self.left.read_raw(),
            self.middle.read_raw(),
            self.right.read_raw(),
        )

    def read_values(self) -> tuple[float, float, float]:
        return tuple([convert(v) for v in self.read_raw_values()])
