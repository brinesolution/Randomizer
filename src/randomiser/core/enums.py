from __future__ import annotations

from enum import Enum


class SourceName(str, Enum):
    CAMERA = "camera"
    MICROPHONE = "microphone"
    CPU_JITTER = "cpu_jitter"
    SCHEDULER_JITTER = "scheduler_jitter"
    OS_RANDOM_BASELINE = "os_random_baseline"


class RunMode(str, Enum):
    WEB = "web"
    BATCH = "batch"
    CLI = "cli"


class RunStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"


class HealthStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
