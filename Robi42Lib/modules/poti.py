from . import base_module


class Poti(base_module.BaseModule):

    conf = {
        'poti': 6
    }

    def __init__(self) -> None:
        self.poti_pin = base_module.AnalogBoardPin('poti')

    def get_raw_value(self) -> int:
        return self.poti_pin.read()

    def get_value(self) -> float:
        raw = self.get_raw_value()
        if raw < 50:
            return 0
        if raw > 974:
            return 1
        return raw / 0b1111111111
