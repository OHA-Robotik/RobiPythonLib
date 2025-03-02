from .... import robi42

class AbstractFrameData:

    @property
    def bytes(self) -> bytes:
        raise NotImplementedError()

    @staticmethod
    def sample(robi: robi42.Robi42) -> "AbstractFrameData":
        raise NotImplementedError()
