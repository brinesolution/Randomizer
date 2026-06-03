from __future__ import annotations

from collections.abc import Iterable


def ensure_bytes(value: bytes | bytearray | memoryview) -> bytes:
    return bytes(value)


def ints_to_low_byte_stream(values: Iterable[int]) -> bytes:
    return bytes(value & 0xFF for value in values)


def low_bits_from_ints(values: Iterable[int], bit_count: int = 2) -> bytes:
    if bit_count <= 0 or bit_count > 8:
        raise ValueError("bit_count must be between 1 and 8")

    mask = (1 << bit_count) - 1
    output = bytearray()
    current = 0
    used_bits = 0

    for value in values:
        current |= (int(value) & mask) << used_bits
        used_bits += bit_count
        while used_bits >= 8:
            output.append(current & 0xFF)
            current >>= 8
            used_bits -= 8

    if used_bits:
        output.append(current & 0xFF)

    return bytes(output)
