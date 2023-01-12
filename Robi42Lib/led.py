from Robi42Lib.mcps import led_and_extension_mcp

HEADLIGHT_LEFT = 0
HEADLIGHT_RIGHT = 1
BLINKER_FRONT_LEFT = 2
BLINKER_FRONT_RIGHT = 3
BLINKER_BACK_LEFT = 4
BLINKER_BACK_RIGHT = 5
BACKLIGHT_LEFT = 6
BACKLIGHT_RIGHT = 7
LED_NUMS = (
    HEADLIGHT_LEFT,
    HEADLIGHT_RIGHT,
    BLINKER_FRONT_LEFT,
    BLINKER_FRONT_RIGHT,
    BLINKER_BACK_RIGHT,
    BLINKER_BACK_LEFT,
    BACKLIGHT_LEFT,
    BACKLIGHT_RIGHT,
)
LED_NUMS_CLOCKWISE = (
    BLINKER_FRONT_LEFT,
    HEADLIGHT_LEFT,
    HEADLIGHT_RIGHT,
    BLINKER_FRONT_RIGHT,
    BLINKER_BACK_RIGHT,
    BACKLIGHT_RIGHT,
    BACKLIGHT_LEFT,
    BLINKER_BACK_LEFT,
)


class Led:

    __state: int

    def __init__(self, led_num: int):
        assert 0 <= led_num < 8, f"Bad led_num: {led_num}"
        self.led_num = led_num
        self.off()

    def on(self):
        led_and_extension_mcp.digital_write(self.led_num, 0)
        self.__state = 0

    def off(self):
        led_and_extension_mcp.digital_write(self.led_num, 1)
        self.__state = 1

    def value(self, value: int):
        assert value == 0 or value == 1
        led_and_extension_mcp.digital_write(self.led_num, value)
        self.__state = value

    def toggle(self):
        self.__state ^= 1
        led_and_extension_mcp.digital_write(self.__state)

    @property
    def state(self):
        return self.__state


class Leds:
    def __init__(self) -> None:
        self.leds = [Led(i) for i in LED_NUMS_CLOCKWISE]

    def all_on(self):
        for led in self.leds:
            led.on()

    def all_off(self):
        for led in self.leds:
            led.off()

    def led_on(self, led_num: int):
        self.leds[led_num].on()

    def led_off(self, led_num: int):
        self.leds[led_num].off()

    def headlight_on(self):
        self.leds[HEADLIGHT_LEFT].on()
        self.leds[HEADLIGHT_RIGHT].on()

    def headlight_off(self):
        self.leds[HEADLIGHT_LEFT].off()
        self.leds[HEADLIGHT_RIGHT].off()

    def backlight_on(self):
        self.leds[BACKLIGHT_LEFT].on()
        self.leds[BACKLIGHT_RIGHT].on()

    def backlight_off(self):
        self.leds[BACKLIGHT_LEFT].off()
        self.leds[BACKLIGHT_RIGHT].off()
