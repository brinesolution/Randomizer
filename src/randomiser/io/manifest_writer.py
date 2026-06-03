from __future__ import annotations

import json
from pathlib import Path

from randomiser.core.models import ExperimentManifest


def manifest_to_dict(manifest: ExperimentManifest) -> dict[str, object]:
    return {
        "experiment_id": manifest.experiment_id,
        "mode": manifest.mode.value,
        "config_name": manifest.config_name,
        "started_at": manifest.started_at.isoformat(),
        "source_names": [source_name.value for source_name in manifest.source_names],
    }


def write_manifest(experiment_dir: str | Path, manifest: ExperimentManifest) -> Path:
    manifest_path = Path(experiment_dir) / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest_to_dict(manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path
