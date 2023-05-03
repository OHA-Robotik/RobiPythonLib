from Robi42Lib.mcps import analog_mcp


class VoltageReader:
    def __init__(self) -> None:
        pass

    def get_battery_voltage(self):
        """Returns the battery voltage in V"""
        return analog_mcp.read(5) / 45.45

    def get_5v_voltage(self):
        return analog_mcp.read(4) / 126

    def get_33v_voltage(self):
        return analog_mcp.read(3) / 184
