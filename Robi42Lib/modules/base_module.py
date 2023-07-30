import hardware_manager.platform_description as pltfm_desc


# redefine for easy access the Hardware
DigitalBoardPin = pltfm_desc.DigitalBoardPin
AnalogBoardPin = pltfm_desc.AnalogBoardPin
BoardDevices = pltfm_desc.BoardDevices


class BaseModule:
    ...
