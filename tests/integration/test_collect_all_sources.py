from __future__ import annotations

from randomiser.core.enums import SourceName
from randomiser.pipeline.parallel_collector import collect_sources
from randomiser.sources import (
    CPUJitterSource,
    CameraSource,
    MicrophoneSource,
    SchedulerJitterSource,
)


def test_collect_all_laptop_sources_with_real_hardware() -> None:
    sources = [
        CameraSource(),
        MicrophoneSource(duration_ms=20),
        CPUJitterSource(iterations=512),
        SchedulerJitterSource(thread_count=2, samples_per_thread=128),
    ]

    result = collect_sources(sources, "run_000001")

    assert result.errors == {}
    assert {sample.source_name for sample in result.samples} == {
        SourceName.CAMERA,
        SourceName.MICROPHONE,
        SourceName.CPU_JITTER,
        SourceName.SCHEDULER_JITTER,
    }
    assert all(sample.raw_bytes for sample in result.samples)
