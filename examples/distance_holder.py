import Robi42Lib


robi = Robi42Lib.Robi42()
robi.begin()

robi.motors.left.disable()
robi.motors.right.disable()

robi.motors.left.set_freq(3000)
robi.motors.right.set_freq(3000)

last_lcd_val = 0

def zfl(s, width):
    # Pads the provided string with leading 0's to suit the specified 'chrs' length
    # Force # characters, fill with leading 0's
    return '{:0>{w}}'.format(s, w=width)

while True:
    distance = int(robi.laser_sensor.read_distance_mm())

    if distance != last_lcd_val:
        robi.lcd.set_cursor(0, 0)
        robi.lcd.put_str(zfl(distance, 4))
        last_lcd_val = distance

    if distance < 190:
        robi.motors.left.set_direction(False)
        robi.motors.right.set_direction(False)
        robi.motors.left.enable()
        robi.motors.right.enable()
    elif distance > 210:
        robi.motors.left.set_direction(True)
        robi.motors.right.set_direction(True)
        robi.motors.left.enable()
        robi.motors.right.enable()
    else:
        robi.motors.left.disable()
        robi.motors.right.disable()
