from Robi42Lib.mcps import analog_mcp


class IrSensor:

    def __init__(self, pin: int) -> None:
        self.__pin = pin

    def read_raw_value(self) -> int:
        return analog_mcp.read(self.__pin)

    def read_value(self) -> float:
        raw = self.read_raw_value()
        if raw < 100:
            return 0
        if raw > 924:
            return 1
        return raw / 0b1111111111


class IrSensors:
    def __init__(self) -> None:
        self.left = IrSensor(0)
        self.middle = IrSensor(1)
        self.right = IrSensor(2)

    def read_raw_values(self) -> tuple[int, int, int]:
        return (
            self.left.read_raw_value(),
            self.middle.read_raw_value(),
            self.right.read_raw_value(),
        )

    def read_values(self) -> tuple[float, float, float]:
        return self.left.read_value(), self.middle.read_value(), self.right.read_value()
