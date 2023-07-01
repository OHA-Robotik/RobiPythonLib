from Robi42Lib.mcps import led_and_extension_mcp

HEADLIGHT_LEFT = 0
HEADLIGHT_RIGHT = 1
BLINKER_FRONT_LEFT = 2
BLINKER_FRONT_RIGHT = 3
BLINKER_BACK_LEFT = 4
BLINKER_BACK_RIGHT = 5
BACKLIGHT_LEFT = 6
BACKLIGHT_RIGHT = 7
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

    __is_on: bool

    def __init__(self, led_num: int):
        assert 0 <= led_num < 8, f"Bad led_num: {led_num}"
        self.led_num = led_num

    def turn_on(self):
        led_and_extension_mcp.digital_write(self.led_num, 0)
        self.__is_on = False

    def turn_off(self):
        led_and_extension_mcp.digital_write(self.led_num, 1)
        self.__is_on = True

    def set_on(self, on: bool):
        led_and_extension_mcp.digital_write(self.led_num, on)
        self.__is_on = on

    def toggle(self):
        self.__is_on ^= 1
        led_and_extension_mcp.digital_write(self.__is_on)

    @property
    def is_on(self):
        return self.__is_on


class LedGroup:
    def __init__(self, leds: list[Led]):
        self.leds = leds

    def turn_on(self):
        for led in self.leds:
            led.turn_on()

    def turn_off(self):
        for led in self.leds:
            led.turn_off()

    def toggle(self):
        for led in self.leds:
            led.toggle()


class Leds:
    def __init__(self) -> None:
        self.leds = [Led(i) for i in LED_NUMS_CLOCKWISE]

        self.blinker_front_left = self.leds[0]
        self.headlight_left = self.leds[1]
        self.headlight_right = self.leds[2]
        self.blinker_front_right = self.leds[3]
        self.blinker_back_right = self.leds[4]
        self.backlight_right = self.leds[5]
        self.backlight_left = self.leds[6]
        self.blinker_back_left = self.leds[7]

        self.headlights = LedGroup([self.headlight_left, self.headlight_right])
        self.backlights = LedGroup([self.backlight_left, self.backlight_right])

    def turn_all_on(self):
        for led in self.leds:
            led.turn_on()

    def turn_all_off(self):
        for led in self.leds:
            led.turn_off()

    def turn_led_on(self, led_num: int):
        self.leds[led_num].turn_on()

    def turn_led_off(self, led_num: int):
        self.leds[led_num].turn_off()
