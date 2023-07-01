from Robi42Lib.mcps import analog_mcp


class Poti:
    def __init__(self) -> None:
        pass

    def get_raw_value(self) -> int:
        return analog_mcp.read(6)

    def get_value(self) -> float:
        raw = self.get_raw_value()
        if raw < 50:
            return 0
        if raw > 974:
            return 1
        return raw / 0b1111111111
