from __future__ import annotations

import json
from datetime import datetime, timezone

from randomiser.core.enums import RunMode, SourceName
from randomiser.core.models import ExperimentManifest
from randomiser.io.artifact_namer import (
    format_experiment_id,
    format_run_id,
    source_input_relative_path,
)
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.manifest_writer import write_manifest


def test_artifact_names_are_stable_and_match_storage_contract() -> None:
    moment = datetime(2026, 6, 4, 8, 30, 5, tzinfo=timezone.utc)

    assert format_experiment_id(moment) == "exp_20260604_083005"
    assert format_run_id(1) == "run_000001"
    assert source_input_relative_path(SourceName.CAMERA, "run_000001").as_posix() == (
        "input/camera/run_000001.bin"
    )


def test_create_experiment_structure_creates_required_directories(tmp_path) -> None:
    experiment_dir = create_experiment_structure(
        tmp_path,
        "exp_test",
        source_names=[
            SourceName.CAMERA,
            SourceName.MICROPHONE,
            SourceName.CPU_JITTER,
            SourceName.SCHEDULER_JITTER,
        ],
    )

    assert experiment_dir == tmp_path / "exp_test"
    assert (experiment_dir / "input" / "camera").is_dir()
    assert (experiment_dir / "input" / "microphone").is_dir()
    assert (experiment_dir / "input" / "cpu_jitter").is_dir()
    assert (experiment_dir / "input" / "scheduler_jitter").is_dir()
    assert (experiment_dir / "output").is_dir()
    assert (experiment_dir / "logs").is_dir()


def test_write_manifest_serializes_experiment_metadata(tmp_path) -> None:
    experiment_dir = create_experiment_structure(tmp_path, "exp_test")
    manifest = ExperimentManifest(
        experiment_id="exp_test",
        mode=RunMode.BATCH,
        config_name="config/default.yaml",
        started_at=datetime(2026, 6, 4, 8, 30, tzinfo=timezone.utc),
        source_names=[SourceName.CAMERA, SourceName.CPU_JITTER],
    )

    manifest_path = write_manifest(experiment_dir, manifest)

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload == {
        "experiment_id": "exp_test",
        "mode": "batch",
        "config_name": "config/default.yaml",
        "started_at": "2026-06-04T08:30:00+00:00",
        "source_names": ["camera", "cpu_jitter"],
    }
