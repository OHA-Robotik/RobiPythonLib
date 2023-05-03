from Robi42Lib.robi42 import Robi42


with Robi42(
    enable_gyro=False,
    enable_ir_sensors=False,
    enable_laser_sensor=False,
    enable_motors=False,
) as r:
    if r.buttons.center.is_pressed():
        from Robi42Lib.AdminMenu import admin_menu

        admin_menu.MainMenu(r).goto()
    else:
        # TODO: only init these if they are connected
        r.init_gyro()
        r.init_ir_sensors()
        r.init_laser_sensor()
        r.init_motors()
