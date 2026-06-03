from __future__ import annotations

from datetime import datetime, timezone

import pytest

from randomiser.core.enums import SourceName
from randomiser.core.models import SourceSample
from randomiser.pipeline.features import (
    calculate_bit_balance,
    estimate_lag1_autocorrelation,
    estimate_shannon_entropy,
    extract_features,
)


def make_sample(raw_bytes: bytes, metadata: dict[str, object] | None = None) -> SourceSample:
    return SourceSample(
        source_name=SourceName.CPU_JITTER,
        run_id="run_000001",
        raw_bytes=raw_bytes,
        collected_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
        duration_ms=1.5,
        metadata=metadata or {},
    )


def test_extract_features_reports_source_byte_metrics_and_metadata() -> None:
    sample = make_sample(b"\x0f\xf0", {"iterations": 2})

    features = extract_features(sample)

    assert features.source_name is SourceName.CPU_JITTER
    assert features.byte_count == 2
    assert features.bit_balance == 0.5
    assert features.unique_byte_count == 2
    assert features.entropy_estimate == pytest.approx(1.0)
    assert -1.0 <= features.autocorrelation <= 1.0
    assert features.extra == {"iterations": 2}


def test_feature_helpers_handle_empty_and_short_inputs() -> None:
    assert calculate_bit_balance(b"") == 0.0
    assert estimate_shannon_entropy(b"") == 0.0
    assert estimate_lag1_autocorrelation(b"\x01") == 0.0


def test_shannon_entropy_detects_constant_and_varied_bytes() -> None:
    assert estimate_shannon_entropy(b"\x00" * 64) == 0.0
    assert estimate_shannon_entropy(bytes(range(256))) == pytest.approx(8.0)
