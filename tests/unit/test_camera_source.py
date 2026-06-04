from __future__ import annotations

from randomiser.core.enums import SourceName
from randomiser.sources.camera_source import CameraSource


def test_camera_source_collects_from_real_laptop_camera() -> None:
    source = CameraSource()

    sample = source.collect("run_000001")

    assert sample.source_name is SourceName.CAMERA
    assert sample.run_id == "run_000001"
    assert len(sample.raw_bytes) > 0
    assert "frame_shape" in sample.metadata
    assert sample.metadata["mean_pixel"] >= 0
    assert sample.metadata["std_pixel"] >= 0
    assert source.last_frame is not None
    assert source.last_frame.size > 0
    assert source.is_available() is True
