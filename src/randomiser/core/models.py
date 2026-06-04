from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from randomiser.core.enums import HealthStatus, RunMode, RunStatus, SourceName


@dataclass(slots=True)
class SourceSample:
    source_name: SourceName
    run_id: str
    raw_bytes: bytes
    collected_at: datetime
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceFeatures:
    source_name: SourceName
    byte_count: int
    bit_balance: float
    entropy_estimate: float
    unique_byte_count: int
    autocorrelation: float
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HealthResult:
    source_name: SourceName
    status: HealthStatus
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PipelineTraceStep:
    name: str
    status: RunStatus
    message: str
    input_ref: str | None = None
    output_ref: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SeedRunResult:
    run_id: str
    mode: RunMode
    seed_hex: str
    status: RunStatus
    source_files: dict[str, str] = field(default_factory=dict)
    health: dict[str, HealthResult] = field(default_factory=dict)
    features: dict[str, SourceFeatures] = field(default_factory=dict)
    trace: list[PipelineTraceStep] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass(slots=True)
class ExperimentManifest:
    experiment_id: str
    mode: RunMode
    config_name: str
    started_at: datetime
    source_names: list[SourceName] = field(default_factory=list)
