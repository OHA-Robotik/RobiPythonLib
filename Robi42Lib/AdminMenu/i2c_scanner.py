from Robi42Lib.AdminMenu.admin_menu import SubmenuList, Menu
from Robi42Lib.i2c_connections import *
from Robi42Lib.robi42 import Robi42
from time import sleep


class HardwareScannerMenu(SubmenuList):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList):
        super().__init__("HW Scanner", robi, origin, [GyroScanMenu(robi, self), LaserAndConnectorsScanMenu(robi, self)])


class GyroScanMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Gyro", "", robi, origin)

    def main_loop(self):

        scanned_addresses = gyro_and_led_i2c.scan()

        self.robi.lcd.clear()

        if scanned_addresses[0] == 0x68:
            self.robi.lcd.putstr("Gyro is connected")
        else:
            self.robi.lcd.putstr("Gyro is not connected")

        while not self.robi.buttons.left.is_pressed():
            sleep(0.1)


class LaserAndConnectorsScanMenu(Menu):
    def __init__(self, robi: Robi42, origin: Menu | SubmenuList | None):
        super().__init__("Laser & conns", "", robi, origin)

    def main_loop(self):

        scanned_addresses = laser_and_conns_i2c.scan()

        self.robi.lcd.clear()

        self.robi.lcd.putstr("Cnct devices:")
        self.robi.lcd.move_to(0, 1)

        for sa in scanned_addresses:
            if sa == 0x3F:
                self.robi.lcd.putstr("LCD ")
            elif sa == 0x29:
                self.robi.lcd.putstr("Laser ")
            else:
                self.robi.lcd.putstr(hex(sa))

        if not scanned_addresses:
            self.robi.lcd.putstr("None")

        while not self.robi.buttons.left.is_pressed():
            sleep(0.1)
