from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from randomiser.core.hashing import sha512_digest

DOMAIN = b"randomiser.conditioner.v1"


def _canonical_json(value: Mapping[str, Any] | None) -> bytes:
    return json.dumps(value or {}, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _part(name: str, value: bytes) -> bytes:
    name_bytes = name.encode("utf-8")
    return (
        len(name_bytes).to_bytes(2, "big")
        + name_bytes
        + len(value).to_bytes(8, "big")
        + value
    )


def condition_fused_bytes(
    fused_bytes: bytes,
    *,
    run_id: str,
    context: Mapping[str, Any] | None = None,
) -> bytes:
    payload = b"".join(
        [
            DOMAIN,
            _part("run_id", run_id.encode("utf-8")),
            _part("context_digest", sha512_digest(_canonical_json(context))),
            _part("fused_bytes", fused_bytes),
        ]
    )
    return sha512_digest(payload)
