from Robi42Lib.rsrc.impl.frame_data import (
    poti,
    abstract,
    buttons,
    motors,
    enabled_feature_set as efs,
)
from . import utils
from Robi42Lib import robi42


class RSRCFrame:

    SOP = 0x7E
    EOP = 0x7F

    SOP_BYTE = SOP.to_bytes(1, "big")
    EOP_BYTE = EOP.to_bytes(1, "big")

    MAX_FRAME_ID = 2**24 - 1

    def __init__(
        self,
        *,
        frame_id: int,
        poti_frame_data: poti.PotiFrameData | None = None,
        buttons_frame_data: buttons.ButtonsFrameData | None = None,
        motors_frame_data: motors.MotorsFrameData | None = None,
        laser_sensor_frame_data: None = None,
        infrared_sensors_frame_data: None = None,
        voltages_frame_data: None = None,
        gyroscope_frame_data: None = None,
        accelerometer_frame_data: None = None,
        led_frame_data: None = None,
        piezo_frame_data: None = None,
        lcd_frame_data: None = None,
    ):
        self.frame_id = frame_id
        self.enabled_feature_set = efs.EnabledFeatureSetFrameData(
            enable_poti_state=poti_frame_data is not None,
            enable_button_states=buttons_frame_data is not None,
            enable_motor_states=motors_frame_data is not None,
            enable_laser_sensor_state=laser_sensor_frame_data is not None,
            enable_infrared_sensors_state=infrared_sensors_frame_data is not None,
            enable_voltages=voltages_frame_data is not None,
            enable_gyroscope_state=gyroscope_frame_data is not None,
            enable_accelerometer_state=accelerometer_frame_data is not None,
            enable_led_states=led_frame_data is not None,
            enable_piezo_state=piezo_frame_data is not None,
            enable_lcd_state=lcd_frame_data is not None,
        )

        self.poti_frame_data = poti_frame_data
        self.buttons_frame_data = buttons_frame_data
        self.motors_frame_data = motors_frame_data

    def as_bytes(self) -> bytes:

        enabled_features: list[abstract.AbstractFrameData] = []

        # Important: The order of the features in the frame is important
        """
        - Voltages
        - Motor states
        - Gyroscope state
        - Accelerometer state
        - Laser sensor state
        - Infrared sensors state
        - Poti state
        - Button states
        - LED states
        - Piezo state
        - LCD display state
        """

        if self.enabled_feature_set.enable_motor_states:
            enabled_features.append(self.motors_frame_data)
        if self.enabled_feature_set.enable_poti_state:
            enabled_features.append(self.poti_frame_data)
        if self.enabled_feature_set.enable_button_states:
            enabled_features.append(self.buttons_frame_data)

        return (
            self.SOP_BYTE
            + utils.to_bytes(self.frame_id, self.MAX_FRAME_ID)
            + self.enabled_feature_set.bytes
            + b"".join(feature.bytes for feature in enabled_features)
            + self.EOP_BYTE
        )

    @staticmethod
    def sample(robi: robi42.Robi42, frame_id: int) -> "RSRCFrame":
        return RSRCFrame(
            frame_id=frame_id,
            poti_frame_data=poti.PotiFrameData.sample(robi),
            buttons_frame_data=buttons.ButtonsFrameData.sample(robi),
            motors_frame_data=motors.MotorsFrameData.sample(robi),
        )
