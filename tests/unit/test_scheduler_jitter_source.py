from __future__ import annotations

from randomiser.core.enums import SourceName
from randomiser.sources.scheduler_jitter_source import SchedulerJitterSource


def test_scheduler_jitter_source_collects_yield_timing_deltas() -> None:
    source = SchedulerJitterSource(
        thread_count=2,
        samples_per_thread=16,
    )

    sample = source.collect("run_000001")

    assert sample.source_name is SourceName.SCHEDULER_JITTER
    assert sample.run_id == "run_000001"
    assert len(sample.raw_bytes) == 32
    assert sample.metadata["thread_count"] == 2
    assert sample.metadata["samples_per_thread"] == 16
    assert sample.metadata["min_delta_ns"] >= 0
    assert sample.metadata["max_delta_ns"] >= sample.metadata["min_delta_ns"]
    assert len(source.last_deltas) == 32
    assert len(source.last_thread_deltas) == 2
    assert source.is_available() is True
