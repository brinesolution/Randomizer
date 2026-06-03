from __future__ import annotations

import csv
import json
from argparse import Namespace
from pathlib import Path


def inspect_experiment_command(args: Namespace) -> int:
    experiment_dir = Path(args.experiment_dir)
    manifest_path = experiment_dir / "manifest.json"
    output_path = experiment_dir / "output" / "run_index.csv"

    if not experiment_dir.exists():
        raise FileNotFoundError(f"Experiment not found: {experiment_dir}")

    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    row_count = 0
    if output_path.exists():
        with output_path.open(newline="", encoding="utf-8") as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))

    experiment_id = manifest.get("experiment_id", experiment_dir.name)
    print(f"experiment: {experiment_id}")
    print(f"path: {experiment_dir}")
    print(f"rows: {row_count}")
    print(f"output: {output_path}")
    return 0
