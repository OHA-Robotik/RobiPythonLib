from . import utils

class RSRCHandshake:

    SOP = 0x7E
    EOP = 0x7F

    SOP_BYTE = SOP.to_bytes(1, "big")
    EOP_BYTE = EOP.to_bytes(1, "big")

    MAX_PROTOCOL_VERSION = 2**8 - 1
    MAX_MSDT = 2 ** 16 - 1

    def __init__(self, *, protocol_version: int, msdt: int):
        assert 0 < protocol_version <= self.MAX_PROTOCOL_VERSION
        assert 0 <= msdt <= self.MAX_MSDT
        self.protocol_version_bytes = utils.to_bytes(protocol_version, self.MAX_PROTOCOL_VERSION)
        self.msdt_bytes = utils.to_bytes(msdt, self.MAX_MSDT)

    def as_bytes(self) -> bytes:
        return self.SOP_BYTE + self.protocol_version_bytes + self.msdt_bytes + self.EOP_BYTE
