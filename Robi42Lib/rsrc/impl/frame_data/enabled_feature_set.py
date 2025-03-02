from . import abstract
from .. import utils

"""
The enabled feature set is communicated as an 16-bit unsigned integer. Each bit represents a feature:

| Bit Position | Feature                |
|--------------|------------------------|
| 0 (MSB)      | Voltages               |
| 1            | Motor States           |
| 2            | Gyroscope State        |
| 3            | Accelerometer State    |
| 4            | Laser Sensor State     |
| 5            | Infrared Sensors State |
| 6            | Poti State             |
| 7            | Button States          |
| 8            | LED States             |
| 9            | Piezo State            |
| 10           | LCD State              |
"""


class EnabledFeatureSetFrameData(abstract.AbstractFrameData):

    MAX_VALUE = 2**16 - 1

    def __init__(
        self,
        *,
        enable_voltages: bool,
        enable_motor_states: bool,
        enable_gyroscope_state: bool,
        enable_accelerometer_state: bool,
        enable_laser_sensor_state: bool,
        enable_infrared_sensors_state: bool,
        enable_poti_state: bool,
        enable_button_states: bool,
        enable_led_states: bool,
        enable_piezo_state: bool,
        enable_lcd_state: bool
    ):
        self.enable_voltages = enable_voltages
        self.enable_motor_states = enable_motor_states
        self.enable_gyroscope_state = enable_gyroscope_state
        self.enable_accelerometer_state = enable_accelerometer_state
        self.enable_laser_sensor_state = enable_laser_sensor_state
        self.enable_infrared_sensors_state = enable_infrared_sensors_state
        self.enable_poti_state = enable_poti_state
        self.enable_button_states = enable_button_states
        self.enable_led_states = enable_led_states
        self.enable_piezo_state = enable_piezo_state
        self.enable_lcd_state = enable_lcd_state

        self.enabled_features_bytes = utils.to_bytes(
            enable_voltages << 15
            | enable_motor_states << 14
            | enable_gyroscope_state << 13
            | enable_accelerometer_state << 12
            | enable_laser_sensor_state << 11
            | enable_infrared_sensors_state << 10
            | enable_poti_state << 9
            | enable_button_states << 8
            | enable_led_states << 7
            | enable_piezo_state << 6
            | enable_lcd_state << 5,
            self.MAX_VALUE,
        )

    @property
    def bytes(self) -> bytes:
        return self.enabled_features_bytes
