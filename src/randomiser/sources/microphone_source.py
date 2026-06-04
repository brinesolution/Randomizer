from __future__ import annotations

from typing import Any

import numpy as np

from randomiser.core.enums import SourceName
from randomiser.core.exceptions import SourceCollectionError
from randomiser.integrations.microphone_backend import SoundDeviceMicrophoneBackend
from randomiser.sources.base import EntropySource
from randomiser.sources.source_helpers import low_bits_from_ints


class MicrophoneSource(EntropySource):
    name = SourceName.MICROPHONE

    def __init__(
        self,
        backend: Any | None = None,
        duration_ms: int = 50,
        sample_rate: int = 16_000,
        bit_count: int = 2,
    ) -> None:
        self.backend = backend or SoundDeviceMicrophoneBackend()
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.bit_count = bit_count
        self.last_samples: np.ndarray | None = None

    def is_available(self) -> bool:
        return bool(self.backend.is_available())

    def collect(self, run_id: str):
        if not self.is_available():
            raise SourceCollectionError("Microphone source is not available")

        samples = self.backend.record(self.duration_ms, self.sample_rate)
        if samples is None:
            raise SourceCollectionError("Microphone source returned no samples")

        captured = np.asarray(samples, dtype=np.int16).ravel()
        self.last_samples = captured.copy()
        array = captured.astype(np.int64)
        if array.size == 0:
            raise SourceCollectionError("Microphone source returned an empty sample block")

        deltas = np.diff(array, append=array[-1])
        metadata = {
            "sample_rate": self.sample_rate,
            "duration_ms": self.duration_ms,
            "sample_count": int(array.size),
            "mean_amplitude": float(np.abs(array).mean()),
        }
        raw_bytes = low_bits_from_ints(deltas, bit_count=self.bit_count)
        return self.build_sample(run_id, raw_bytes, metadata=metadata)
