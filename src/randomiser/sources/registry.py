from __future__ import annotations

from randomiser.sources.camera_source import CameraSource
from randomiser.sources.cpu_jitter_source import CPUJitterSource
from randomiser.sources.microphone_source import MicrophoneSource
from randomiser.sources.os_random_baseline import OSRandomBaselineSource
from randomiser.sources.scheduler_jitter_source import SchedulerJitterSource

SOURCE_REGISTRY = {
    "camera": CameraSource,
    "microphone": MicrophoneSource,
    "cpu_jitter": CPUJitterSource,
    "scheduler_jitter": SchedulerJitterSource,
    "os_random_baseline": OSRandomBaselineSource,
}


def build_source(name: str, **kwargs):
    try:
        source_class = SOURCE_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(SOURCE_REGISTRY))
        raise ValueError(f"Unknown source '{name}'. Available sources: {available}") from exc
    return source_class(**kwargs)
