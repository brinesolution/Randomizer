from __future__ import annotations

import wave
from datetime import datetime, timezone

import numpy as np

from randomiser.core.enums import HealthStatus, SourceName
from randomiser.core.models import HealthResult, SourceSample
from randomiser.trace.web_visuals import (
    build_sample_visual,
    build_transformation_visual,
    save_camera_previews,
    save_microphone_preview,
)


def sample(source_name: SourceName, raw_bytes: bytes) -> SourceSample:
    return SourceSample(
        source_name=source_name,
        run_id="run_000001",
        raw_bytes=raw_bytes,
        collected_at=datetime.now(timezone.utc),
        duration_ms=1.0,
        metadata={"demo": True},
    )


def test_build_sample_visual_returns_compact_chart_data() -> None:
    visual = build_sample_visual(sample(SourceName.CPU_JITTER, bytes(range(256))))

    assert len(visual["series"]) <= 128
    assert sum(item["count"] for item in visual["histogram"]) == 256
    assert len(visual["lagPairs"]) <= 64
    assert visual["hexPreview"].startswith("00 01 02 03")


def test_preview_writers_persist_camera_conversions_and_audio(tmp_path) -> None:
    frame = np.zeros((8, 8, 3), dtype=np.uint8)
    frame[:, :, 1] = 120
    camera_paths = save_camera_previews(tmp_path, "run_000001", frame, bit_count=2)
    audio_path = save_microphone_preview(
        tmp_path,
        "run_000001",
        np.array([0, 200, -200, 100], dtype=np.int16),
        sample_rate=8000,
    )

    assert (tmp_path / camera_paths["original"]).exists()
    assert (tmp_path / camera_paths["grayscale"]).exists()
    assert (tmp_path / camera_paths["lowBits"]).exists()
    assert (tmp_path / audio_path).exists()
    with wave.open(str(tmp_path / audio_path), "rb") as audio:
        assert audio.getframerate() == 8000
        assert audio.getnframes() == 4


def test_transformation_visual_matches_pipeline_otp() -> None:
    samples = [
        sample(SourceName.CPU_JITTER, b"\x01\x02\x03\x04"),
        sample(SourceName.SCHEDULER_JITTER, b"\x05\x06\x07\x08"),
    ]
    health = {
        source.source_name.value: HealthResult(source.source_name, HealthStatus.PASS, 1.0)
        for source in samples
    }
    visual = build_transformation_visual(
        samples,
        health,
        run_id="run_000001",
        context={"experiment_id": "exp_demo", "mode": "web", "config_hash": "abc"},
    )

    assert len(visual["sourceHashes"]) == 2
    assert visual["sourceHashes"][0]["rawPreview"] == [1, 2, 3, 4]
    assert visual["sourceHashes"][1]["rawPreview"] == [5, 6, 7, 8]
    assert len(visual["fusedDigest"]) == 128
    assert len(visual["conditionedDigest"]) == 128
    assert visual["seedHex"] == visual["conditionedDigest"]
