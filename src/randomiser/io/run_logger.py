from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from randomiser.core.models import SeedRunResult, SourceSample
from randomiser.io.input_store import save_source_samples
from randomiser.io.output_index import append_output_row


def log_run(
    experiment_dir: str | Path,
    result: SeedRunResult,
    samples: list[SourceSample],
) -> SeedRunResult:
    source_files = save_source_samples(experiment_dir, samples)
    logged_result = replace(result, source_files={**result.source_files, **source_files})
    append_output_row(experiment_dir, logged_result)
    return logged_result
