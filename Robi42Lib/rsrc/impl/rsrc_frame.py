from Robi42Lib.rsrc.impl.frame_data import poti, abstract, buttons, enabled_feature_set as efs
from . import utils

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
    ):
        self.frame_id = frame_id
        self.enabled_feature_set = efs.EnabledFeatureSetFrameData(
            enable_poti_state=poti_frame_data is not None,
            enable_button_states=buttons_frame_data is not None,
        )
        self.poti_frame_data = poti_frame_data
        self.buttons_frame_data = buttons_frame_data

    def as_bytes(self) -> bytes:

        enabled_features: list[abstract.AbstractFrameData] = []

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
