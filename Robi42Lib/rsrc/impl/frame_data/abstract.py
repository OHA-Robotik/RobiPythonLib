class AbstractFrameData:

    @property
    def bytes(self) -> bytes:
        raise NotImplementedError()
