from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

from randomiser.core.enums import RunMode, RunStatus, SourceName
from randomiser.core.models import ExperimentManifest, OtpRunResult
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.manifest_writer import write_manifest
from randomiser.io.run_logger import log_run


def test_fake_run_writes_structured_experiment_dataset(
    temp_experiments_root,
    fake_source_samples,
) -> None:
    experiment_dir = create_experiment_structure(temp_experiments_root, "exp_dataset")
    manifest = ExperimentManifest(
        experiment_id="exp_dataset",
        mode=RunMode.BATCH,
        config_name="config/laptop_mvp.yaml",
        started_at=datetime(2026, 6, 4, 8, 30, tzinfo=timezone.utc),
        source_names=[
            SourceName.CAMERA,
            SourceName.MICROPHONE,
            SourceName.CPU_JITTER,
            SourceName.SCHEDULER_JITTER,
        ],
    )
    write_manifest(experiment_dir, manifest)

    result = OtpRunResult(
        run_id="run_000001",
        mode=RunMode.BATCH,
        otp="123456",
        status=RunStatus.OK,
        created_at=datetime(2026, 6, 4, 8, 32, tzinfo=timezone.utc),
    )

    logged = log_run(experiment_dir, result, fake_source_samples)

    assert json.loads((experiment_dir / "manifest.json").read_text(encoding="utf-8"))["experiment_id"] == (
        "exp_dataset"
    )
    for sample in fake_source_samples:
        folder = sample.source_name.value
        assert (experiment_dir / "input" / folder / "run_000001.bin").read_bytes() == sample.raw_bytes
        assert logged.source_files[sample.source_name.value] == f"input/{folder}/run_000001.bin"

    with (experiment_dir / "output" / "run_index.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["run_id"] == "run_000001"
    assert rows[0]["otp"] == "123456"
    assert rows[0]["camera_input_file"] == "input/camera/run_000001.bin"
    assert rows[0]["microphone_input_file"] == "input/microphone/run_000001.bin"
    assert rows[0]["cpu_jitter_input_file"] == "input/cpu_jitter/run_000001.bin"
    assert rows[0]["scheduler_jitter_input_file"] == "input/scheduler_jitter/run_000001.bin"
