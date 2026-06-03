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


def run_web_once(
    sources: Iterable[EntropySource],
    *,
    experiments_root: str | Path,
    experiment_id: str,
    config_name: str = "web_mode",
    min_required_sources: int = DEFAULT_MIN_HEALTHY_SOURCES,
    config: dict[str, Any] | None = None,
) -> OtpRunResult:
    source_list = list(sources)
    experiment_dir = create_experiment_structure(
        experiments_root,
        experiment_id,
        source_names=[source.name for source in source_list],
    )
    write_manifest(
        experiment_dir,
        ExperimentManifest(
            experiment_id=experiment_id,
            mode=RunMode.WEB,
            config_name=config_name,
            started_at=datetime.now(timezone.utc),
            source_names=[source.name for source in source_list],
        ),
    )

    context = build_run_context(1, mode=RunMode.WEB, experiment_id=experiment_id, config=config)
    result, samples = EntropyManager(
        source_list,
        min_required_sources=min_required_sources,
    ).generate_once_with_samples(context)
    return log_run(experiment_dir, result, samples)
