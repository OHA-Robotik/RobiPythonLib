from Robi42Lib.mcps import analog_mcp


def to_voltage(X, ref_voltage):
    """Convert a measurement integer to a voltage.
        MCP3008: 1023 = VREF
    """
    return (X / 1023) * ref_voltage


def spannungsteiler(u_in, r1, r2):
    """Berechne die Spannung am ADC, wenn du die Spannung am Eingang kennst."""
    return u_in * (1 / (1 + r2/r1))


def spannungsteiler_reverse(u_out, r1, r2):
    """Berechne die Spannung am Eingang, wenn du die spannung am ADC kennst."""
    return u_out * (1 + r2/r1)


class VoltageReader:

    REF_VOLTAGE = 2.5

    def __init__(self) -> None:
        self.magic_bat = 1 / spannungsteiler_reverse(to_voltage(1, ref_voltage=self.REF_VOLTAGE), r1=2.2, r2=22)
        self.magic_50v = 1 / spannungsteiler_reverse(to_voltage(1, ref_voltage=self.REF_VOLTAGE), r1=2.2, r2=4.7)
        self.magic_33v = 1 / spannungsteiler_reverse(to_voltage(1, ref_voltage=self.REF_VOLTAGE), r1=2.2, r2=2.7)

    def get_battery_voltage(self):
        """Returns the battery voltage in V"""
        return analog_mcp.read(5) / self.magic_bat

    def get_5v_voltage(self):
        """Returns the 5V voltage in V"""
        return analog_mcp.read(5) / self.magic_50v

    def get_33v_voltage(self):
        """Returns the 3.3V voltage in V"""
        return analog_mcp.read(5) / self.magic_33v
