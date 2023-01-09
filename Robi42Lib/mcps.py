from Robi42Lib.spi_connections import *
from Robi42Lib.lib.mcp import MCP23S17

# Led and extension mcp

led_and_extension_mcp = MCP23S17(
    ce=led_and_motor_cs, deviceID=0x00, spi_interface=led_and_motor_spi
)
led_and_extension_mcp.open()

for i in range(16):
    led_and_extension_mcp.setDirection(i, led_and_extension_mcp.DIR_OUTPUT)


# Motor and taster mcp

motor_and_taster_mcp = MCP23S17(
    ce=led_and_motor_cs, deviceID=0x01, spi_interface=led_and_motor_spi
)
motor_and_taster_mcp.open()

for i in range(8):
    motor_and_taster_mcp.setDirection(i, motor_and_taster_mcp.DIR_OUTPUT)

for i in range(8, 13):
    motor_and_taster_mcp.setDirection(i, motor_and_taster_mcp.DIR_INPUT)

for i in range(14, 16):
    motor_and_taster_mcp.setDirection(i, motor_and_taster_mcp.DIR_OUTPUT)

