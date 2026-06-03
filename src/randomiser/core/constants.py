from __future__ import annotations

from randomiser.core.enums import SourceName

OTP_RANGE = 1_000_000
OTP_DIGITS = 6
DEFAULT_MIN_HEALTHY_SOURCES = 2

SOURCE_FOLDER_NAMES = {
    SourceName.CAMERA: "camera",
    SourceName.MICROPHONE: "microphone",
    SourceName.CPU_JITTER: "cpu_jitter",
    SourceName.SCHEDULER_JITTER: "scheduler_jitter",
    SourceName.OS_RANDOM_BASELINE: "os_random_baseline",
}
