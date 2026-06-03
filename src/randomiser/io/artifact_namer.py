from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from randomiser.core.constants import SOURCE_FOLDER_NAMES
from randomiser.core.enums import SourceName


def format_experiment_id(started_at: datetime | None = None) -> str:
    timestamp = started_at or datetime.now(timezone.utc)
    return f"exp_{timestamp.strftime('%Y%m%d_%H%M%S')}"


def format_run_id(run_number: int) -> str:
    if run_number < 1:
        raise ValueError("run_number must be positive")
    return f"run_{run_number:06d}"


def source_input_relative_path(source_name: SourceName, run_id: str) -> Path:
    folder_name = SOURCE_FOLDER_NAMES[source_name]
    return Path("input") / folder_name / f"{run_id}.bin"


def output_index_relative_path() -> Path:
    return Path("output") / "run_index.csv"
