from . import base_module


class _LedGroup:
    """
    Represents a group of LEDs that can be controlled together.
    """

    def __init__(self, leds: list[base_module.DigitalBoardPin]):
        """
        Initializes a new LED group.

        Args:
            leds (list[base_module.DigitalBoardPin]): A list of digital pins controlling the LEDs.
        """
        self.__pins = leds

    def on(self):
        """
        Turns all LEDs in the group ON.
        """
        for led in self.__pins:
            led.off() #  LEDs are active low

    def off(self):
        """
        Turns all LEDs in the group OFF.
        """
        for led in self.__pins:
            led.on() # Note: LEDs are active low

    def toggle(self):
        """
        Toggles the state of all LEDs in the group.
        """
        for led in self.__pins:
            led.value(not led.value()) # LEDs are active low

    def value(self, level: bool):
        """
        Sets all LEDs in the group to a specific state.

        Args:
            level (bool): `True` to turn LEDs OFF, `False` to turn them ON.
        """
        for led_pin in self.__pins:
            led_pin.value(not level)  #  LEDs are active low


class Leds(base_module.BaseModule):
    """
    Controls the LED system of the Robi42 robot.

    This module allows individual control over different LED groups,
    such as headlights, blinkers, and backlights.
    """

    def __init__(self):
        """
        Initializes the LED module and creates LED groups.
        """
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
        self.all = _LedGroup(
            [
                h_l_pin,
                h_r_pin,
                b_l_pin,
                b_r_pin,
                bl_fl_pin,
                bl_fr_pin,
                bl_bl_pin,
                bl_br_pin,
            ]
        )

    def begin(self):
        self.all.off()
