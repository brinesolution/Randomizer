from __future__ import annotations

from collections.abc import Iterable

from randomiser.core.enums import HealthStatus
from randomiser.core.models import HealthResult, SourceFeatures, SourceSample
from randomiser.pipeline.features import extract_features
from randomiser.pipeline.health_tests import run_health_tests


def evaluate_source_health(
    sample: SourceSample,
    features: SourceFeatures | None = None,
) -> HealthResult:
    source_features = features or extract_features(sample)
    return run_health_tests(sample, source_features)


def evaluate_sources(samples: Iterable[SourceSample]) -> dict[str, HealthResult]:
    return {
        sample.source_name.value: evaluate_source_health(sample)
        for sample in samples
    }


def passed_sources(
    samples: Iterable[SourceSample],
    health_results: dict[str, HealthResult],
) -> list[SourceSample]:
    return [
        sample
        for sample in samples
        if health_results.get(sample.source_name.value, None) is not None
        and health_results[sample.source_name.value].status is HealthStatus.PASS
    ]
