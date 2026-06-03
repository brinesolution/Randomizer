from __future__ import annotations

import time
from collections.abc import Callable

from randomiser.core.enums import SourceName
from randomiser.sources.base import EntropySource
from randomiser.sources.source_helpers import ints_to_low_byte_stream


class CPUJitterSource(EntropySource):
    name = SourceName.CPU_JITTER

    def __init__(self, iterations: int = 512, clock_ns: Callable[[], int] | None = None) -> None:
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        self.iterations = iterations
        self.clock_ns = clock_ns or time.perf_counter_ns

    def collect(self, run_id: str):
        deltas: list[int] = []
        previous = self.clock_ns()

        for index in range(self.iterations):
            _ = (index * index) ^ (index + 17)
            current = self.clock_ns()
            deltas.append(max(0, current - previous))
            previous = current

        metadata = {
            "iterations": self.iterations,
            "min_delta_ns": min(deltas),
            "max_delta_ns": max(deltas),
            "mean_delta_ns": sum(deltas) / len(deltas),
        }
        return self.build_sample(run_id, ints_to_low_byte_stream(deltas), metadata=metadata)
