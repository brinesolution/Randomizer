from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Iterable

from randomiser.core.models import SourceSample
from randomiser.sources.base import EntropySource


@dataclass(slots=True)
class CollectionResult:
    samples: list[SourceSample] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)


def collect_sources(
    sources: Iterable[EntropySource],
    run_id: str,
    *,
    max_workers: int | None = None,
) -> CollectionResult:
    source_list = list(sources)
    if not source_list:
        return CollectionResult()

    result = CollectionResult()
    workers = max_workers or len(source_list)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(source.collect, run_id): source for source in source_list}
        for future in as_completed(futures):
            source = futures[future]
            try:
                result.samples.append(future.result())
            except Exception as exc:
                result.errors[source.name.value] = str(exc)

    result.samples.sort(key=lambda sample: sample.source_name.value)
    return result
