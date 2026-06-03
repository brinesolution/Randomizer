from __future__ import annotations

from datetime import datetime, timezone

import pytest

from randomiser.core.enums import HealthStatus, SourceName
from randomiser.core.exceptions import HealthGateError
from randomiser.core.models import HealthResult, SourceSample
from randomiser.pipeline.hg_msef import fuse_healthy_sources, fuse_source_hashes
from randomiser.pipeline.source_hasher import hash_source_sample


def make_sample(
    source_name: SourceName,
    raw_bytes: bytes,
    *,
    run_id: str = "run_000001",
) -> SourceSample:
    return SourceSample(
        source_name=source_name,
        run_id=run_id,
        raw_bytes=raw_bytes,
        collected_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
        duration_ms=1.0,
        metadata={"length": len(raw_bytes)},
    )


def test_source_hash_includes_name_run_bytes_and_metadata() -> None:
    sample = make_sample(SourceName.CPU_JITTER, b"source-bytes")

    digest = hash_source_sample(sample)

    assert isinstance(digest, bytes)
    assert len(digest) == 64
    assert digest == hash_source_sample(sample)
    assert digest != hash_source_sample(make_sample(SourceName.CPU_JITTER, b"changed"))
    assert digest != hash_source_sample(make_sample(SourceName.SCHEDULER_JITTER, b"source-bytes"))


def test_fusion_is_sorted_by_source_name_not_input_order() -> None:
    camera_hash = b"c" * 64
    cpu_hash = b"a" * 64

    first = fuse_source_hashes(
        {
            SourceName.CAMERA: camera_hash,
            SourceName.CPU_JITTER: cpu_hash,
        },
        run_id="run_000001",
    )
    second = fuse_source_hashes(
        {
            SourceName.CPU_JITTER: cpu_hash,
            SourceName.CAMERA: camera_hash,
        },
        run_id="run_000001",
    )

    assert first == second
    assert len(first) == 64


def test_fusion_changes_when_source_input_changes() -> None:
    first = fuse_source_hashes(
        {SourceName.CPU_JITTER: hash_source_sample(make_sample(SourceName.CPU_JITTER, b"one"))},
        run_id="run_000001",
    )
    second = fuse_source_hashes(
        {SourceName.CPU_JITTER: hash_source_sample(make_sample(SourceName.CPU_JITTER, b"two"))},
        run_id="run_000001",
    )

    assert first != second


def test_fuse_healthy_sources_uses_pass_and_warn_sources_only() -> None:
    passed = make_sample(SourceName.CPU_JITTER, b"passed")
    warned = make_sample(SourceName.SCHEDULER_JITTER, b"warned")
    failed = make_sample(SourceName.CAMERA, b"failed")
    health = {
        SourceName.CPU_JITTER.value: HealthResult(SourceName.CPU_JITTER, HealthStatus.PASS, 1.0),
        SourceName.SCHEDULER_JITTER.value: HealthResult(SourceName.SCHEDULER_JITTER, HealthStatus.WARN, 0.8),
        SourceName.CAMERA.value: HealthResult(SourceName.CAMERA, HealthStatus.FAIL, 0.0, ["bad"]),
    }

    fused = fuse_healthy_sources([failed, warned, passed], health, run_id="run_000001")
    expected = fuse_source_hashes(
        {
            SourceName.CPU_JITTER: hash_source_sample(passed),
            SourceName.SCHEDULER_JITTER: hash_source_sample(warned),
        },
        run_id="run_000001",
    )

    assert fused == expected


def test_fuse_healthy_sources_rejects_empty_accepted_set() -> None:
    failed = make_sample(SourceName.CAMERA, b"failed")
    health = {
        SourceName.CAMERA.value: HealthResult(SourceName.CAMERA, HealthStatus.FAIL, 0.0, ["bad"]),
    }

    with pytest.raises(HealthGateError):
        fuse_healthy_sources([failed], health, run_id="run_000001")
