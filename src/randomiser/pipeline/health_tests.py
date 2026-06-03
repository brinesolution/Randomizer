from __future__ import annotations

from randomiser.core.enums import HealthStatus
from randomiser.core.models import HealthResult, SourceFeatures, SourceSample
from randomiser.pipeline.features import extract_features

DEFAULT_MIN_UNIQUE_BYTES = 4
DEFAULT_MIN_ENTROPY = 1.0
DEFAULT_MIN_BIT_BALANCE = 0.20
DEFAULT_MAX_BIT_BALANCE = 0.80


def run_health_tests(
    sample: SourceSample,
    features: SourceFeatures | None = None,
    *,
    min_unique_bytes: int = DEFAULT_MIN_UNIQUE_BYTES,
    min_entropy: float = DEFAULT_MIN_ENTROPY,
    min_bit_balance: float = DEFAULT_MIN_BIT_BALANCE,
    max_bit_balance: float = DEFAULT_MAX_BIT_BALANCE,
) -> HealthResult:
    source_features = features or extract_features(sample)
    reasons: list[str] = []

    if source_features.byte_count == 0:
        reasons.append("empty data")

    if source_features.byte_count > 0 and source_features.unique_byte_count == 1:
        reasons.append("constant data")

    if source_features.unique_byte_count < min_unique_bytes:
        reasons.append("unique byte count below threshold")

    if not min_bit_balance <= source_features.bit_balance <= max_bit_balance:
        reasons.append("bit balance outside threshold")

    if source_features.entropy_estimate < min_entropy:
        reasons.append("entropy estimate below threshold")

    check_count = 5
    score = max(0.0, (check_count - len(reasons)) / check_count)
    status = HealthStatus.PASS if not reasons else HealthStatus.FAIL

    return HealthResult(
        source_name=sample.source_name,
        status=status,
        score=score,
        reasons=reasons,
    )
