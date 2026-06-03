from __future__ import annotations

from collections.abc import Iterable

from randomiser.core.models import HealthResult
from randomiser.pipeline.features import extract_features
from randomiser.pipeline.health_gate import evaluate_source_health
from randomiser.pipeline.parallel_collector import collect_sources
from randomiser.sources.base import EntropySource


def calibrate_sources(
    sources: Iterable[EntropySource],
    *,
    run_id: str = "calibration",
) -> dict[str, HealthResult]:
    collection = collect_sources(sources, run_id)
    results: dict[str, HealthResult] = {}

    for sample in collection.samples:
        features = extract_features(sample)
        results[sample.source_name.value] = evaluate_source_health(sample, features)

    return results
