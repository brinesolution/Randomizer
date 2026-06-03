from __future__ import annotations

from collections.abc import Iterable

from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.core.enums import HealthStatus, RunStatus
from randomiser.core.models import HealthResult


def count_passed_sources(health_results: Iterable[HealthResult]) -> int:
    return sum(1 for result in health_results if result.status is HealthStatus.PASS)


def decide_run_status(
    health_results: Iterable[HealthResult],
    *,
    min_required_sources: int = DEFAULT_MIN_HEALTHY_SOURCES,
) -> RunStatus:
    results = list(health_results)
    if not results:
        return RunStatus.FAILED

    passed_count = count_passed_sources(results)
    if passed_count == len(results):
        return RunStatus.OK

    if passed_count >= min_required_sources:
        return RunStatus.DEGRADED

    return RunStatus.FAILED
