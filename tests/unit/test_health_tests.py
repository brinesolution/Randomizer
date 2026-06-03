from __future__ import annotations

from datetime import datetime, timezone

from randomiser.core.enums import HealthStatus, RunStatus, SourceName
from randomiser.core.models import HealthResult, SourceSample
from randomiser.pipeline.degraded_mode import decide_run_status
from randomiser.pipeline.health_gate import evaluate_source_health


def make_sample(raw_bytes: bytes, source_name: SourceName = SourceName.CPU_JITTER) -> SourceSample:
    return SourceSample(
        source_name=source_name,
        run_id="run_000001",
        raw_bytes=raw_bytes,
        collected_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
        duration_ms=1.0,
    )


def test_health_gate_fails_empty_data() -> None:
    health = evaluate_source_health(make_sample(b""))

    assert health.status is HealthStatus.FAIL
    assert health.score < 1.0
    assert "empty data" in health.reasons


def test_health_gate_fails_all_zero_and_constant_data() -> None:
    zero_health = evaluate_source_health(make_sample(b"\x00" * 64))
    constant_health = evaluate_source_health(make_sample(b"\xff" * 64))

    assert zero_health.status is HealthStatus.FAIL
    assert constant_health.status is HealthStatus.FAIL
    assert "constant data" in zero_health.reasons
    assert "constant data" in constant_health.reasons


def test_health_gate_passes_reasonable_random_like_data() -> None:
    health = evaluate_source_health(make_sample(bytes(range(256))))

    assert health.status is HealthStatus.PASS
    assert health.score == 1.0
    assert health.reasons == []


def test_degraded_mode_decides_ok_degraded_and_failed() -> None:
    first_pass = HealthResult(SourceName.CPU_JITTER, HealthStatus.PASS, 1.0)
    second_pass = HealthResult(SourceName.SCHEDULER_JITTER, HealthStatus.PASS, 1.0)
    failed = HealthResult(SourceName.CAMERA, HealthStatus.FAIL, 0.0, ["empty data"])

    assert decide_run_status([first_pass, second_pass], min_required_sources=2) is RunStatus.OK
    assert decide_run_status([first_pass, failed], min_required_sources=1) is RunStatus.DEGRADED
    assert decide_run_status([failed], min_required_sources=1) is RunStatus.FAILED
