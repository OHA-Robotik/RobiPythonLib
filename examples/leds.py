import time
import Robi42Lib


robi = Robi42Lib.Robi42()
robi.begin()

leds_in_order = [
    robi.leds.headlight_right,
    robi.leds.blinker_front_right,
    robi.leds.blinker_back_right,
    robi.leds.backlight_right,
    robi.leds.backlight_left,
    robi.leds.blinker_back_left,
    robi.leds.blinker_front_left,
    robi.leds.headlight_left,
]


robi.leds.all.off()
for _ in range(3):
    for led in leds_in_order:
        led.on()
        time.sleep(0.1)
        led.off()

while True:
    robi.leds.headlights.on()
    robi.leds.backlights.on()
    time.sleep(3)
    for _ in range(6):
        robi.leds.blinker_back_right.on()
        robi.leds.blinker_front_right.on()
        time.sleep(0.3)
        robi.leds.blinker_back_right.off()
        robi.leds.blinker_front_right.off()
        time.sleep(0.3)
    time.sleep(3)
    for _ in range(6):
        robi.leds.blinker_back_left.on()
        robi.leds.blinker_front_left.on()
        time.sleep(0.3)
        robi.leds.blinker_back_left.off()
        robi.leds.blinker_front_left.off()
        time.sleep(0.3)
