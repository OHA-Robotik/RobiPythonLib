from Robi42Lib.mcps import analog_mcp


class VoltageReader:
    def __init__(self) -> None:
        pass

    def get_battery_voltage(self):
        """Returns the battery voltage in V"""
        return analog_mcp.read(5) / 37.2

    def get_5v_voltage(self):
        return analog_mcp.read(4) / 130.46956521739133

    def get_33v_voltage(self):
        return analog_mcp.read(3) / 183.72244897959183

    def get_33v_voltage_c(self):
        return analog_mcp.read(3) / 225.47755102040816
