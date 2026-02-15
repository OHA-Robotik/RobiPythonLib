import Robi42Lib


robi = Robi42Lib.Robi42()
robi.begin()

robi.motors.left.enable()
robi.motors.right.enable()

threshold = 200
while True:
    raw_l, raw_m , raw_r = robi.ir_sensors.read_raw_values()

    l_dark = raw_l < threshold
    m_dark = raw_m < threshold
    r_dark = raw_r < threshold

    if m_dark:
        if not l_dark and not r_dark:
            robi.motors.left.set_freq(5000)
            robi.motors.right.set_freq(5000)
        elif l_dark and not r_dark:
            robi.motors.left.set_freq(2000)
            robi.motors.right.set_freq(4000)
        elif r_dark and not l_dark:
            robi.motors.left.set_freq(4000)
            robi.motors.right.set_freq(2000)
    else:
        if l_dark and not r_dark:
            robi.motors.left.set_freq(300)
            robi.motors.right.set_freq(4000)
        elif r_dark and not l_dark:
            robi.motors.left.set_freq(4000)
            robi.motors.right.set_freq(300)
