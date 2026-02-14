from Robi42Lib import robi42
from time import sleep

r = robi42.Robi42()
r.begin()

r.leds.all.on()

r.lcd.turn_on()

output = "Hello!"

if r.external_storage.is_connected():
    output += f"\nHW Rev.: {r.external_storage.read_hw_revision()}"

r.lcd.put_str(output)

while True:
    sleep(1)
