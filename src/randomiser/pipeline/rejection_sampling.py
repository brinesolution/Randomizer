from __future__ import annotations

from randomiser.core.constants import OTP_RANGE
from randomiser.core.hashing import sha512_digest

UINT32_SIZE = 2**32
CHUNK_SIZE = 4


def _chunks(raw_bytes: bytes, chunk_size: int = CHUNK_SIZE) -> list[bytes]:
    return [
        raw_bytes[index:index + chunk_size]
        for index in range(0, len(raw_bytes) - (len(raw_bytes) % chunk_size), chunk_size)
    ]


def rejection_sample_int(seed_bytes: bytes, *, upper_bound: int = OTP_RANGE) -> int:
    if upper_bound <= 0:
        raise ValueError("upper_bound must be positive")

    limit = (UINT32_SIZE // upper_bound) * upper_bound
    current = seed_bytes
    counter = 0

    while True:
        for chunk in _chunks(current):
            candidate = int.from_bytes(chunk, "big")
            if candidate < limit:
                return candidate % upper_bound

        counter += 1
        current = sha512_digest(seed_bytes + counter.to_bytes(8, "big"))
