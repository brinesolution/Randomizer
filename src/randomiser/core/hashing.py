from __future__ import annotations

import hashlib


def sha512_digest(payload: bytes) -> bytes:
    return hashlib.sha512(payload).digest()


def blake2b_digest(payload: bytes, digest_size: int = 64) -> bytes:
    return hashlib.blake2b(payload, digest_size=digest_size).digest()
