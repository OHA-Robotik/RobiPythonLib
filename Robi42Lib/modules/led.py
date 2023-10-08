from . import base_module


class _LedGroup:
    def __init__(self, leds: list[base_module.DigitalBoardPin]):
        self.__pins = leds

    def on(self):
        for led in self.__pins:
            # Because "Gegen Masse"
            led.off()

    def off(self):
        for led in self.__pins:
            # Because "Gegen Masse"
            led.on()

    def toggle(self):
        for led in self.__pins:
            led.value(not led.value())

    def value(self, level: bool):
        for led in self.__pins:
            led.value(level)


class Leds(base_module.BaseModule):
    def __init__(self) -> None:
        h_l_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_sl)
        h_r_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_sr)

        b_l_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_rl)
        b_r_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_rr)

        bl_fl_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_lv)
        bl_fr_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_rv)
        bl_bl_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_lh)
        bl_br_pin = base_module.DigitalBoardPin(base_module.DigitalBoardPins.led_bl_rh)

        self.headlight_left = _LedGroup([h_l_pin])
        self.headlight_right = _LedGroup([h_r_pin])
        self.blinker_front_left = _LedGroup([bl_fl_pin])
        self.blinker_front_right = _LedGroup([bl_fr_pin])
        self.blinker_back_left = _LedGroup([bl_bl_pin])
        self.blinker_back_right = _LedGroup([bl_br_pin])
        self.backlight_left = _LedGroup([b_l_pin])
        self.backlight_right = _LedGroup([b_r_pin])
        self.headlights = _LedGroup([h_l_pin, h_r_pin])
        self.backlights = _LedGroup([b_l_pin, b_r_pin])
        self.blinkers = _LedGroup([bl_fl_pin, bl_fr_pin, bl_bl_pin, bl_br_pin])
        self.all = _LedGroup([h_l_pin, h_r_pin, b_l_pin, b_r_pin, bl_fl_pin, bl_fr_pin, bl_bl_pin, bl_br_pin])
