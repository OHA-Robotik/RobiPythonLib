from Robi42Lib.mcps import analog_mcp


class Poti:
    def __init__(self) -> None:
        pass

    def _get_raw_value(self) -> int:
        return analog_mcp.read(6)

    def get_value(self) -> float:
        raw = self._get_raw_value()
        if raw < 50:
            raw = 0
        elif raw > 974:
            raw = 974
        return raw / 974
