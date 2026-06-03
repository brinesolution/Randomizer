from __future__ import annotations

from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from randomiser.core.config_loader import load_config
from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.core.enums import RunMode
from randomiser.core.models import ExperimentManifest
from randomiser.core.paths import get_project_root
from randomiser.io.artifact_namer import format_experiment_id
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.manifest_writer import write_manifest
from randomiser.io.run_logger import log_run
from randomiser.modes.batch_mode import build_sources_from_config
from randomiser.pipeline.entropy_manager import EntropyManager
from randomiser.pipeline.run_context import build_run_context


def resolve_experiments_root(config: dict[str, Any], override: str | None = None) -> Path:
    root = Path(override or config["experiment"]["base_dir"])
    if root.is_absolute():
        return root
    return get_project_root() / root


def run_once_command(args: Namespace) -> int:
    config = load_config(args.config)
    sources = build_sources_from_config(config)
    experiments_root = resolve_experiments_root(config, args.experiments_root)
    experiment_id = args.experiment_id or format_experiment_id()
    min_required_sources = config["sources"].get("min_healthy_sources", DEFAULT_MIN_HEALTHY_SOURCES)

    experiment_dir = create_experiment_structure(
        experiments_root,
        experiment_id,
        source_names=[source.name for source in sources],
    )
    write_manifest(
        experiment_dir,
        ExperimentManifest(
            experiment_id=experiment_id,
            mode=RunMode.CLI,
            config_name=str(args.config),
            started_at=datetime.now(timezone.utc),
            source_names=[source.name for source in sources],
        ),
    )

    context = build_run_context(1, mode=RunMode.CLI, experiment_id=experiment_id, config=config)
    result, samples = EntropyManager(
        sources,
        min_required_sources=min_required_sources,
    ).generate_once_with_samples(context)
    logged = log_run(experiment_dir, result, samples)

    print(f"OTP: {logged.otp}")
    print(f"status: {logged.status.value}")
    print(f"experiment: {experiment_dir}")
    return 0
