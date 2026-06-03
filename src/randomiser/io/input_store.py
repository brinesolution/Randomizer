from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from randomiser.core.models import SourceSample
from randomiser.io.artifact_namer import source_input_relative_path


def _relative_posix(path: Path) -> str:
    return path.as_posix()


def save_source_sample(experiment_dir: str | Path, sample: SourceSample) -> str:
    relative_path = source_input_relative_path(sample.source_name, sample.run_id)
    output_path = Path(experiment_dir) / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(sample.raw_bytes)
    return _relative_posix(relative_path)


def save_source_samples(
    experiment_dir: str | Path,
    samples: Iterable[SourceSample],
) -> dict[str, str]:
    return {
        sample.source_name.value: save_source_sample(experiment_dir, sample)
        for sample in samples
    }
