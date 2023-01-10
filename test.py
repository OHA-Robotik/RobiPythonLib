from Robi42Lib.robi42 import Robi42
from time import sleep

with Robi42() as r:

    r.lcd.on()
    for i in range(1, 6):
        r.lcd.putstr(f"Start in {5-i}s")
        sleep(1)
        r.lcd.clear()
    r.lcd.off()

    r.motor_left.enable()
    # r.motor_right.enable()

    # r.motor_right.set_freq(10000)
    r.motor_left.set_freq(10000)

    """
    for i in range(20_000, 150_000, 1000):
        r.motor_right.set_freq(i)
        r.motor_left.set_freq(i)
        print("Freq:", i)
        sleep(0.1)
    """

    while True:
        sleep(1)
