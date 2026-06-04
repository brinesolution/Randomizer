from __future__ import annotations

import csv
from datetime import datetime, timezone

from randomiser.core.enums import RunMode, RunStatus, SourceName
from randomiser.core.models import SeedRunResult, SourceSample
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.run_logger import log_run


def make_sample(source_name: SourceName, raw_bytes: bytes, run_id: str = "run_000001") -> SourceSample:
    return SourceSample(
        source_name=source_name,
        run_id=run_id,
        raw_bytes=raw_bytes,
        collected_at=datetime(2026, 6, 4, 8, 31, tzinfo=timezone.utc),
        duration_ms=2.0,
    )


def test_log_run_writes_four_input_files_and_one_output_row(tmp_path) -> None:
    experiment_dir = create_experiment_structure(tmp_path, "exp_test")
    samples = [
        make_sample(SourceName.CAMERA, b"camera"),
        make_sample(SourceName.MICROPHONE, b"microphone"),
        make_sample(SourceName.CPU_JITTER, b"cpu"),
        make_sample(SourceName.SCHEDULER_JITTER, b"scheduler"),
    ]
    result = SeedRunResult(
        run_id="run_000001",
        mode=RunMode.BATCH,
        seed_hex="ab" * 64,
        status=RunStatus.OK,
        created_at=datetime(2026, 6, 4, 8, 32, tzinfo=timezone.utc),
    )

    logged = log_run(experiment_dir, result, samples)

    assert logged.source_files == {
        "camera": "input/camera/run_000001.bin",
        "microphone": "input/microphone/run_000001.bin",
        "cpu_jitter": "input/cpu_jitter/run_000001.bin",
        "scheduler_jitter": "input/scheduler_jitter/run_000001.bin",
    }
    assert (experiment_dir / logged.source_files["camera"]).read_bytes() == b"camera"
    assert (experiment_dir / logged.source_files["microphone"]).read_bytes() == b"microphone"
    assert (experiment_dir / logged.source_files["cpu_jitter"]).read_bytes() == b"cpu"
    assert (experiment_dir / logged.source_files["scheduler_jitter"]).read_bytes() == b"scheduler"

    with (experiment_dir / "output" / "run_index.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "run_id": "run_000001",
            "mode": "batch",
            "camera_input_file": "input/camera/run_000001.bin",
            "microphone_input_file": "input/microphone/run_000001.bin",
            "cpu_jitter_input_file": "input/cpu_jitter/run_000001.bin",
            "scheduler_jitter_input_file": "input/scheduler_jitter/run_000001.bin",
            "seed_hex": "ab" * 64,
            "status": "ok",
            "created_at": "2026-06-04T08:32:00+00:00",
        }
    ]
