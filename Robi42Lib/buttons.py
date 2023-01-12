from Robi42Lib.mcps import motor_and_button_mcp


class Button:
    def __init__(self, mcp_gpb: int):
        self.mcp_gpb = mcp_gpb

    def is_pressed(self) -> bool:
        return motor_and_button_mcp.digital_read(self.mcp_gpb)
