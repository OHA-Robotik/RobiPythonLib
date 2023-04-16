from machine import SPI, Pin

led_and_motor_cs = Pin(13, Pin.OUT)
led_and_motor_spi = SPI(
    1,
    baudrate=1000000,
    polarity=1,
    phase=1,
    bits=8,
    firstbit=SPI.MSB,
    sck=Pin(10),
    mosi=Pin(11),
    miso=Pin(12),
)

analog_cs = Pin(5, Pin.OUT)
analog_spi = SPI(
    0,
    baudrate=1000000,
    polarity=1,
    phase=1,
    bits=8,
    firstbit=SPI.MSB,
    sck=Pin(2),
    mosi=Pin(3),
    miso=Pin(4),
)
