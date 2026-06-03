from __future__ import annotations

from typing import Any

import numpy as np

from randomiser.core.enums import SourceName
from randomiser.core.exceptions import SourceCollectionError
from randomiser.integrations.camera_backend import OpenCVCameraBackend
from randomiser.sources.base import EntropySource
from randomiser.sources.source_helpers import low_bits_from_ints


class CameraSource(EntropySource):
    name = SourceName.CAMERA

    def __init__(self, backend: Any | None = None, bit_count: int = 2) -> None:
        self.backend = backend or OpenCVCameraBackend()
        self.bit_count = bit_count

    def is_available(self) -> bool:
        return bool(self.backend.is_available())

    def collect(self, run_id: str):
        if not self.is_available():
            raise SourceCollectionError("Camera source is not available")

        frame = self.backend.capture_frame()
        if frame is None:
            raise SourceCollectionError("Camera source returned no frame")

        array = np.asarray(frame)
        if array.size == 0:
            raise SourceCollectionError("Camera source returned an empty frame")
        if array.ndim == 3:
            array = array.mean(axis=2).astype(np.uint8)

        metadata = {
            "frame_shape": tuple(array.shape),
            "mean_pixel": float(array.mean()),
            "std_pixel": float(array.std()),
        }
        raw_bytes = low_bits_from_ints(array.astype(np.uint8).ravel(), bit_count=self.bit_count)
        return self.build_sample(run_id, raw_bytes, metadata=metadata)
