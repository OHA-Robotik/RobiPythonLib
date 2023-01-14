from Robi42Lib.spi_connections import *
from Robi42Lib.lib.mcp import MCP23S17

# Led and extension mcp

led_and_extension_mcp = MCP23S17(led_and_motor_cs, 1, led_and_motor_spi)
led_and_extension_mcp.open()

for i in range(16):
    led_and_extension_mcp.set_direction(i, led_and_extension_mcp.DIR_OUTPUT)


# Motor and button mcp

motor_and_button_mcp = MCP23S17(led_and_motor_cs, 0, led_and_motor_spi
)
motor_and_button_mcp.open()

for i in range(8):
    motor_and_button_mcp.set_direction(i, motor_and_button_mcp.DIR_OUTPUT)

for i in range(8, 13):
    motor_and_button_mcp.set_direction(i, motor_and_button_mcp.DIR_INPUT)
    motor_and_button_mcp.set_pullup_PORTB(0b00111111)

for i in range(14, 16):
    motor_and_button_mcp.set_direction(i, motor_and_button_mcp.DIR_OUTPUT)
