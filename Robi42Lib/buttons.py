from Robi42Lib.mcps import motor_and_button_mcp


class Button:
    def __init__(self, mcp_gpb: int):
        self.mcp_gpb = mcp_gpb

    def is_pressed(self) -> bool:
        return not motor_and_button_mcp.digital_read(self.mcp_gpb)


class Buttons:
    def __init__(self) -> None:
        self.up = Button(11)
        self.down = Button(12)
        self.center = Button(8)
        self.left = Button(9)
        self.right = Button(10)
