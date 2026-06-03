from __future__ import annotations

from typing import Any


class SoundDeviceMicrophoneBackend:
    def is_available(self) -> bool:
        try:
            import sounddevice as sd

            return bool(sd.query_devices(kind="input"))
        except Exception:
            return False

    def record(self, duration_ms: int, sample_rate: int) -> Any:
        import sounddevice as sd

        frames = max(1, int(sample_rate * duration_ms / 1000))
        data = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
        return data
