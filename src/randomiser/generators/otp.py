from __future__ import annotations

from typing import Any

from randomiser.core.constants import OTP_RANGE
from randomiser.core.hashing import sha512_digest
from randomiser.generators.seed_derivation import derive_child_seed
from randomiser.pipeline.otp_generator import format_otp

UINT32_SIZE = 2**32


def _rejection_details(seed: bytes) -> dict[str, int | bool]:
    limit = (UINT32_SIZE // OTP_RANGE) * OTP_RANGE
    current = seed
    inspected = 0
    round_index = 0
    while True:
        for index in range(0, len(current) - (len(current) % 4), 4):
            candidate = int.from_bytes(current[index:index + 4], "big")
            inspected += 1
            if candidate < limit:
                return {
                    "candidate": candidate,
                    "limit": limit,
                    "accepted": True,
                    "inspected": inspected,
                    "value": candidate % OTP_RANGE,
                }
        round_index += 1
        current = sha512_digest(seed + round_index.to_bytes(8, "big"))


def generate_otp(seed_hex: str) -> dict[str, Any]:
    child_seed = derive_child_seed(seed_hex, "otp")
    rejection = _rejection_details(child_seed)
    return {
        "kind": "otp",
        "otp": format_otp(int(rejection["value"])),
        "rejection": rejection,
        "childSeedHash": sha512_digest(child_seed).hex(),
    }
