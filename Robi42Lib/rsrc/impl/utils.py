def to_bytes(value: int, maximum_value: int) -> bytes:
    bytes_to_reserve = (len(bin(maximum_value)) + 5) // 8
    return value.to_bytes(bytes_to_reserve, "big")
