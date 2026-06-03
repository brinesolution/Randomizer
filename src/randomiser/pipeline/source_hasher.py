from __future__ import annotations

import json

from randomiser.core.hashing import sha512_digest
from randomiser.core.models import SourceSample

DOMAIN = b"randomiser.source_hash.v1"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _part(name: str, value: bytes) -> bytes:
    name_bytes = name.encode("utf-8")
    return (
        len(name_bytes).to_bytes(2, "big")
        + name_bytes
        + len(value).to_bytes(8, "big")
        + value
    )


def hash_source_sample(sample: SourceSample) -> bytes:
    metadata_digest = sha512_digest(_canonical_json(sample.metadata))
    payload = b"".join(
        [
            DOMAIN,
            _part("source_name", sample.source_name.value.encode("utf-8")),
            _part("run_id", sample.run_id.encode("utf-8")),
            _part("raw_bytes", sample.raw_bytes),
            _part("metadata_digest", metadata_digest),
        ]
    )
    return sha512_digest(payload)
