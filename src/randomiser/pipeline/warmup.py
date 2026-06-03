from __future__ import annotations

from collections.abc import Iterable

from randomiser.sources.base import EntropySource


def check_source_availability(sources: Iterable[EntropySource]) -> dict[str, bool]:
    availability: dict[str, bool] = {}
    for source in sources:
        try:
            availability[source.name.value] = bool(source.is_available())
        except Exception:
            availability[source.name.value] = False
    return availability


def unavailable_sources(sources: Iterable[EntropySource]) -> list[str]:
    return [name for name, available in check_source_availability(sources).items() if not available]
