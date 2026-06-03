from __future__ import annotations

from randomiser.core.enums import SourceName
from randomiser.core.models import SourceSample
from randomiser.sources.base import EntropySource
from randomiser.sources.cpu_jitter_source import CPUJitterSource
from randomiser.sources.os_random_baseline import OSRandomBaselineSource
from randomiser.sources.registry import SOURCE_REGISTRY, build_source
from randomiser.sources.source_helpers import ensure_bytes, ints_to_low_byte_stream, low_bits_from_ints


class DemoSource(EntropySource):
    name = SourceName.CPU_JITTER

    def collect(self, run_id: str) -> SourceSample:
        return self.build_sample(run_id, b"\x01\x02", metadata={"demo": True}, duration_ms=0.5)


def test_base_source_builds_sample_with_common_fields() -> None:
    sample = DemoSource().collect("run_000001")

    assert sample.source_name is SourceName.CPU_JITTER
    assert sample.run_id == "run_000001"
    assert sample.raw_bytes == b"\x01\x02"
    assert sample.metadata == {"demo": True}
    assert sample.duration_ms == 0.5


def test_source_helpers_convert_integer_noise_to_bytes() -> None:
    assert ensure_bytes(bytearray([1, 2, 3])) == b"\x01\x02\x03"
    assert ints_to_low_byte_stream([0, 255, 256, 511]) == b"\x00\xff\x00\xff"
    assert low_bits_from_ints([0b00000011, 0b00000010], bit_count=2) == b"\x0b"


def test_cpu_jitter_source_collects_timing_deltas_with_metadata() -> None:
    source = CPUJitterSource(iterations=64)

    sample = source.collect("run_000001")

    assert sample.source_name is SourceName.CPU_JITTER
    assert sample.run_id == "run_000001"
    assert len(sample.raw_bytes) == 64
    assert sample.metadata["iterations"] == 64
    assert sample.metadata["min_delta_ns"] >= 0
    assert sample.metadata["max_delta_ns"] >= sample.metadata["min_delta_ns"]
    assert sample.metadata["mean_delta_ns"] >= 0
    assert source.is_available() is True


def test_os_random_baseline_and_registry_are_available() -> None:
    baseline = OSRandomBaselineSource(sample_size=16)
    sample = baseline.collect("run_000002")

    assert sample.source_name is SourceName.OS_RANDOM_BASELINE
    assert len(sample.raw_bytes) == 16
    assert SOURCE_REGISTRY["cpu_jitter"] is CPUJitterSource
    assert isinstance(build_source("cpu_jitter"), CPUJitterSource)
