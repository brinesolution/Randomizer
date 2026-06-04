from __future__ import annotations

import threading
import time
from collections.abc import Callable

from randomiser.core.enums import SourceName
from randomiser.sources.base import EntropySource
from randomiser.sources.source_helpers import ints_to_low_byte_stream


class SchedulerJitterSource(EntropySource):
    name = SourceName.SCHEDULER_JITTER

    def __init__(
        self,
        thread_count: int = 4,
        samples_per_thread: int = 128,
        clock_ns: Callable[[], int] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if thread_count <= 0:
            raise ValueError("thread_count must be positive")
        if samples_per_thread <= 0:
            raise ValueError("samples_per_thread must be positive")
        self.thread_count = thread_count
        self.samples_per_thread = samples_per_thread
        self.clock_ns = clock_ns or time.perf_counter_ns
        self.sleep_fn = sleep_fn or time.sleep
        self.last_deltas: list[int] = []
        self.last_thread_deltas: list[list[int]] = []

    def collect(self, run_id: str):
        deltas: list[int] = []
        thread_deltas: list[list[int]] = []
        lock = threading.Lock()

        def worker() -> None:
            local_deltas: list[int] = []
            previous = self.clock_ns()
            for _ in range(self.samples_per_thread):
                self.sleep_fn(0)
                current = self.clock_ns()
                local_deltas.append(max(0, current - previous))
                previous = current
            with lock:
                deltas.extend(local_deltas)
                thread_deltas.append(local_deltas)

        threads = [threading.Thread(target=worker) for _ in range(self.thread_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        metadata = {
            "thread_count": self.thread_count,
            "samples_per_thread": self.samples_per_thread,
            "min_delta_ns": min(deltas),
            "max_delta_ns": max(deltas),
            "mean_delta_ns": sum(deltas) / len(deltas),
        }
        self.last_deltas = list(deltas)
        self.last_thread_deltas = [list(values) for values in thread_deltas]
        return self.build_sample(run_id, ints_to_low_byte_stream(deltas), metadata=metadata)
