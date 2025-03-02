from . import abstract
from .. import utils
from .... import robi42

class PotiFrameData(abstract.AbstractFrameData):

    MAX_VALUE = 255

    def __init__(self, *, value: int):
        assert 0 <= value <= self.MAX_VALUE
        self.value_bytes = utils.to_bytes(value, self.MAX_VALUE)

    @property
    def bytes(self) -> bytes:
        return self.value_bytes

    @staticmethod
    def sample(robi: robi42.Robi42) -> "PotiFrameData":
        return PotiFrameData(value=int(robi.poti.get_value() * PotiFrameData.MAX_VALUE))