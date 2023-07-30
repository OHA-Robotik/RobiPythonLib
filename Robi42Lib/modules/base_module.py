import hardware_manager.manager as hw_manager
import hardware_manager.platform_description as pltfm_desc


# redefine for easy access the Hardware
DigitalBoardPin = pltfm_desc.DigitalBoardPin
AnalogBoardPin = pltfm_desc.AnalogBoardPin


def needs_i2c_hardware(driver_name):
    def function_wrapper(func):
        manager_instance = hw_manager.HardwareManager.get_instance()
        def inner_wrap(*args, **kwargs):
            driver = manager_instance.get_i2c_driver_by_name(driver_name)
            func(*args, **args, **{driver_name: driver})
        return inner_wrap
    return function_wrapper

class BaseModule:
    ...
