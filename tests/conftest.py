from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from randomiser.core.enums import SourceName
from randomiser.core.models import SourceSample


@pytest.fixture
def fixed_time() -> datetime:
    return datetime(2026, 6, 4, 8, 30, tzinfo=timezone.utc)


@pytest.fixture
def temp_experiments_root(tmp_path: Path) -> Path:
    return tmp_path / "experiments"


@pytest.fixture
def fake_source_sample(fixed_time):
    def build(source_name: SourceName, raw_bytes: bytes, run_id: str = "run_000001") -> SourceSample:
        return SourceSample(
            source_name=source_name,
            run_id=run_id,
            raw_bytes=raw_bytes,
            collected_at=fixed_time,
            duration_ms=1.0,
            metadata={"test_source": source_name.value},
        )

    return build


@pytest.fixture
def fake_source_samples(fake_source_sample) -> list[SourceSample]:
    return [
        fake_source_sample(SourceName.CAMERA, b"camera"),
        fake_source_sample(SourceName.MICROPHONE, b"microphone"),
        fake_source_sample(SourceName.CPU_JITTER, b"cpu"),
        fake_source_sample(SourceName.SCHEDULER_JITTER, b"scheduler"),
    ]
