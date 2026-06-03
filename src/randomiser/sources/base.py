from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from randomiser.core.enums import SourceName
from randomiser.core.models import SourceSample


class EntropySource(ABC):
    name: SourceName

    def is_available(self) -> bool:
        return True

    @abstractmethod
    def collect(self, run_id: str) -> SourceSample:
        raise NotImplementedError

    def build_sample(
        self,
        run_id: str,
        raw_bytes: bytes,
        metadata: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
    ) -> SourceSample:
        return SourceSample(
            source_name=self.name,
            run_id=run_id,
            raw_bytes=raw_bytes,
            collected_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
