from Robi42Lib.robi42 import Robi42
from time import sleep

with Robi42() as r:

    r.motor_left.enable()
    
    r.motor_left.set_freq(20000)

    while True:
        sleep(1)
