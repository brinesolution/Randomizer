from __future__ import annotations

import argparse
from collections.abc import Sequence

from randomiser.cli.calibrate_cmd import calibrate_command
from randomiser.cli.generate_dataset_cmd import generate_dataset_command
from randomiser.cli.inspect_experiment_cmd import inspect_experiment_command
from randomiser.cli.run_once_cmd import run_once_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="randomiser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_once = subparsers.add_parser("run-once", help="generate and save one seed run")
    run_once.add_argument("--config", default="config/cpu_scheduler_only.yaml")
    run_once.add_argument("--experiments-root", default=None)
    run_once.add_argument("--experiment-id", default=None)
    run_once.add_argument("--output-kind", choices=["otp", "map", "maze"], default=None)
    run_once.set_defaults(handler=run_once_command)

    batch = subparsers.add_parser(
        "batch",
        aliases=["generate-dataset"],
        help="generate and save many seed runs",
    )
    batch.add_argument("--config", default="config/cpu_scheduler_only.yaml")
    batch.add_argument("--runs", type=int, default=None)
    batch.add_argument("--experiments-root", default=None)
    batch.add_argument("--experiment-id", default=None)
    batch.add_argument("--output-kind", choices=["otp", "map", "maze"], default=None)
    batch.set_defaults(handler=generate_dataset_command)

    calibrate = subparsers.add_parser("calibrate", help="check source availability and health")
    calibrate.add_argument("--config", default="config/cpu_scheduler_only.yaml")
    calibrate.set_defaults(handler=calibrate_command)

    inspect = subparsers.add_parser("inspect-experiment", help="print experiment summary")
    inspect.add_argument("experiment_dir")
    inspect.set_defaults(handler=inspect_experiment_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))
