from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.core.enums import RunMode
from randomiser.core.models import ExperimentManifest, OtpRunResult
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.manifest_writer import write_manifest
from randomiser.io.run_logger import log_run
from randomiser.pipeline.entropy_manager import EntropyManager
from randomiser.pipeline.run_context import build_run_context
from randomiser.sources.base import EntropySource
from randomiser.sources.registry import build_source


def build_sources_from_config(config: dict[str, Any]) -> list[EntropySource]:
    return [build_source(source_name) for source_name in config["sources"]["enabled"]]


def run_batch(
    sources: Iterable[EntropySource],
    *,
    experiments_root: str | Path,
    experiment_id: str,
    run_count: int,
    config_name: str,
    min_required_sources: int = DEFAULT_MIN_HEALTHY_SOURCES,
    config: dict[str, Any] | None = None,
) -> list[OtpRunResult]:
    if run_count < 1:
        raise ValueError("run_count must be positive")

    source_list = list(sources)
    experiment_dir = create_experiment_structure(
        experiments_root,
        experiment_id,
        source_names=[source.name for source in source_list],
    )
    manifest = ExperimentManifest(
        experiment_id=experiment_id,
        mode=RunMode.BATCH,
        config_name=config_name,
        started_at=datetime.now(timezone.utc),
        source_names=[source.name for source in source_list],
    )
    write_manifest(experiment_dir, manifest)

    manager = EntropyManager(source_list, min_required_sources=min_required_sources)
    results: list[OtpRunResult] = []
    for run_number in range(1, run_count + 1):
        context = build_run_context(
            run_number,
            mode=RunMode.BATCH,
            experiment_id=experiment_id,
            config=config,
        )
        result, samples = manager.generate_once_with_samples(context)
        logged = log_run(experiment_dir, result, samples)
        results.append(logged)

    return results
