from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from randomiser.core.enums import HealthStatus, SourceName
from randomiser.core.exceptions import HealthGateError
from randomiser.core.hashing import sha512_digest
from randomiser.core.models import HealthResult, SourceSample
from randomiser.pipeline.source_hasher import hash_source_sample

DOMAIN = b"randomiser.hg_msef.v1"


def _source_key(source_name: SourceName | str) -> str:
    return source_name.value if isinstance(source_name, SourceName) else str(source_name)


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


def fuse_source_hashes(
    source_hashes: Mapping[SourceName | str, bytes],
    *,
    run_id: str,
    context: Mapping[str, Any] | None = None,
) -> bytes:
    if not source_hashes:
        raise HealthGateError("no source hashes to fuse")

    parts = [
        DOMAIN,
        _part("run_id", run_id.encode("utf-8")),
        _part("context_digest", sha512_digest(_canonical_json(context))),
    ]
    for source_name, source_hash in sorted(source_hashes.items(), key=lambda item: _source_key(item[0])):
        if not source_hash:
            raise HealthGateError(f"empty hash for source {_source_key(source_name)}")
        parts.append(_part("source_name", _source_key(source_name).encode("utf-8")))
        parts.append(_part("source_hash", source_hash))

    return sha512_digest(b"".join(parts))


def fuse_healthy_sources(
    samples: Sequence[SourceSample],
    health_results: Mapping[str | SourceName, HealthResult],
    *,
    run_id: str | None = None,
    context: Mapping[str, Any] | None = None,
    accept_warn: bool = True,
) -> bytes:
    accepted_statuses = {HealthStatus.PASS}
    if accept_warn:
        accepted_statuses.add(HealthStatus.WARN)

    source_hashes: dict[SourceName, bytes] = {}
    for sample in samples:
        health = health_results.get(sample.source_name.value) or health_results.get(sample.source_name)
        if health is not None and health.status in accepted_statuses:
            source_hashes[sample.source_name] = hash_source_sample(sample)

    if not source_hashes:
        raise HealthGateError("no healthy source samples to fuse")

    resolved_run_id = run_id or samples[0].run_id
    return fuse_source_hashes(source_hashes, run_id=resolved_run_id, context=context)
