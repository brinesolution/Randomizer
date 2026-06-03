from __future__ import annotations

from randomiser.core.enums import SourceName
from randomiser.sources.microphone_source import MicrophoneSource


def test_microphone_source_collects_from_real_laptop_microphone() -> None:
    source = MicrophoneSource(duration_ms=50, sample_rate=8000)

    sample = source.collect("run_000001")

    assert sample.source_name is SourceName.MICROPHONE
    assert sample.run_id == "run_000001"
    assert len(sample.raw_bytes) > 0
    assert sample.metadata["sample_rate"] == 8000
    assert sample.metadata["duration_ms"] == 50
    assert sample.metadata["sample_count"] > 0
    assert sample.metadata["mean_amplitude"] >= 0
    assert source.is_available() is True
