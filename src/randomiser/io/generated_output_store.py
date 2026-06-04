from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from randomiser.generators.service import OUTPUT_KINDS


def save_generated_output(
    experiment_dir: str | Path,
    run_id: str,
    output: dict[str, Any],
) -> Path:
    kind = str(output.get("kind", ""))
    if kind not in OUTPUT_KINDS:
        raise ValueError(f"unsupported output kind: {kind}")
    path = Path(experiment_dir) / "output" / "generated" / kind / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    return path
