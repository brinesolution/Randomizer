from __future__ import annotations

import os

from randomiser.core.enums import SourceName
from randomiser.sources.base import EntropySource


class OSRandomBaselineSource(EntropySource):
    name = SourceName.OS_RANDOM_BASELINE

    def __init__(self, sample_size: int = 64) -> None:
        if sample_size <= 0:
            raise ValueError("sample_size must be positive")
        self.sample_size = sample_size

    def collect(self, run_id: str):
        return self.build_sample(
            run_id,
            os.urandom(self.sample_size),
            metadata={"sample_size": self.sample_size, "baseline": True},
        )
