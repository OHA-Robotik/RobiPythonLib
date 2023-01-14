from Robi42Lib.robi42 import Robi42
from time import sleep

with Robi42() as r:

    r.motors.set_freq(10000)

    while True:

        r.motors.set_direction(r.motors.dir_forward)

        if r.buttons.left.is_pressed():
            r.motors.left.disable()
            r.motors.right.enable()
        elif r.buttons.right.is_pressed():
            r.motors.right.disable()
            r.motors.left.enable()
        elif r.buttons.up.is_pressed():
            r.motors.enable()
        elif r.buttons.down.is_pressed():
            r.motors.set_direction(r.motors.dir_backward)
            r.motors.enable()
        else:
            r.motors.disable()

        sleep(0.1)
