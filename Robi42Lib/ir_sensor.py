from Robi42Lib.mcps import analog_mcp


class IrSensor:
    __pin: int

    def __init__(self, pin: int) -> None:
        self.__pin = pin

    def get_raw_value(self) -> int:
        return analog_mcp.read(self.__pin)

    def get_value(self) -> float:
        raw = self.get_raw_value()
        if raw < 100:
            raw = 0
        elif raw > 924:
            raw = 1024
        return raw / 1024


class IrSensors:
    def __init__(self) -> None:
        self.left = IrSensor(0)
        self.middle = IrSensor(1)
        self.right = IrSensor(2)

    def get_raw_values(self) -> tuple[int, int, int]:
        return (
            self.left.get_raw_value(),
            self.middle.get_raw_value(),
            self.right.get_raw_value(),
        )

    def get_values(self) -> tuple[float, float, float]:
        return self.left.get_value(), self.middle.get_value(), self.right.get_value()
