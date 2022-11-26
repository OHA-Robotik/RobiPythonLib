from machine import I2C, Pin

gyro_and_led_i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
laser_and_conns_i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)
