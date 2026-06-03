from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from randomiser.core.constants import SOURCE_FOLDER_NAMES
from randomiser.core.enums import SourceName


DEFAULT_EXPERIMENT_SOURCES = [
    SourceName.CAMERA,
    SourceName.MICROPHONE,
    SourceName.CPU_JITTER,
    SourceName.SCHEDULER_JITTER,
]


def create_experiment_structure(
    experiments_root: str | Path,
    experiment_id: str,
    *,
    source_names: Iterable[SourceName] | None = None,
) -> Path:
    experiment_dir = Path(experiments_root) / experiment_id
    sources = list(source_names or DEFAULT_EXPERIMENT_SOURCES)

    for source_name in sources:
        (experiment_dir / "input" / SOURCE_FOLDER_NAMES[source_name]).mkdir(parents=True, exist_ok=True)

    (experiment_dir / "output").mkdir(parents=True, exist_ok=True)
    (experiment_dir / "logs").mkdir(parents=True, exist_ok=True)
    return experiment_dir
