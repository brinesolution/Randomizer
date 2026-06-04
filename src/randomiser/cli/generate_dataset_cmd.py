from __future__ import annotations

from argparse import Namespace

from randomiser.core.config_loader import load_config
from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.io.artifact_namer import format_experiment_id
from randomiser.modes.batch_mode import build_sources_from_config, run_batch
from randomiser.cli.run_once_cmd import resolve_experiments_root


def generate_dataset_command(args: Namespace) -> int:
    config = load_config(args.config)
    sources = build_sources_from_config(config)
    run_count = args.runs or config.get("batch", {}).get("runs", 1)
    experiments_root = resolve_experiments_root(config, args.experiments_root)
    experiment_id = args.experiment_id or format_experiment_id()
    min_required_sources = config["sources"].get("min_healthy_sources", DEFAULT_MIN_HEALTHY_SOURCES)

    results = run_batch(
        sources,
        experiments_root=experiments_root,
        experiment_id=experiment_id,
        run_count=run_count,
        config_name=str(args.config),
        min_required_sources=min_required_sources,
        config=config,
        output_kind=args.output_kind,
    )

    print(f"experiment: {experiments_root / experiment_id}")
    print(f"runs: {len(results)}")
    print(f"output: {experiments_root / experiment_id / 'output' / 'run_index.csv'}")
    return 0
