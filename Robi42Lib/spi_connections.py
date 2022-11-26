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
