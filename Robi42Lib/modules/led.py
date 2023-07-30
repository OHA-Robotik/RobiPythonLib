from . import base_module


class LedGroup:
    def __init__(self, leds: list[base_module.DigitalBoardPin]):
        self.leds = leds

    def on(self):
        for led in self.leds:
            led.on()

    def off(self):
        for led in self.leds:
            led.off()


class Leds(base_module.BaseModule):
    def __init__(self) -> None:
        self.headlight_left = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_sl)])
        self.headlight_right = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_sr)])
        self.blinker_front_left = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_lv)])
        self.blinker_front_right = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_rv)])
        self.blinker_back_left = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_lh)])
        self.blinker_back_right = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_rh)])
        self.backlight_left = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_rl)])
        self.backlight_right = LedGroup([base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_rr)])
        self.headlights = LedGroup([self.headlight_left.leds[0], self.headlight_right.leds[0]])
        self.backlights = LedGroup([self.backlight_left.leds[0], self.backlight_right.leds[0]])
        self.all = LedGroup([
            self.blinker_front_left.leds[0],
            self.headlight_left.leds[0],
            self.headlight_right.leds[0],
            self.blinker_front_right.leds[0],
            self.blinker_back_right.leds[0],
            self.backlight_right.leds[0],
            self.backlight_left.leds[0],
            self.blinker_back_left.leds[0],
        ])
