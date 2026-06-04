from __future__ import annotations

from randomiser.core.hashing import sha512_digest

DOMAIN = b"randomiser.output.v1"
MASTER_SEED_BYTES = 64


def parse_master_seed(seed_hex: str) -> bytes:
    try:
        seed = bytes.fromhex(seed_hex)
    except ValueError as exc:
        raise ValueError("master seed must be hexadecimal") from exc
    if len(seed) != MASTER_SEED_BYTES:
        raise ValueError("master seed must contain 64 bytes")
    return seed


def derive_child_seed(seed_hex: str, namespace: str) -> bytes:
    if not namespace or not namespace.isascii():
        raise ValueError("namespace must be non-empty ASCII")
    seed = parse_master_seed(seed_hex)
    namespace_bytes = namespace.encode("ascii")
    payload = (
        DOMAIN
        + len(namespace_bytes).to_bytes(2, "big")
        + namespace_bytes
        + seed
    )
    return sha512_digest(payload)


def expand_seed(seed: bytes, size: int, *, namespace: str) -> bytes:
    if size < 0:
        raise ValueError("size must be non-negative")
    output = bytearray()
    counter = 0
    domain = namespace.encode("ascii")
    while len(output) < size:
        output.extend(sha512_digest(seed + domain + counter.to_bytes(8, "big")))
        counter += 1
    return bytes(output[:size])
