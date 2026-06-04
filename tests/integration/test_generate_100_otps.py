from __future__ import annotations

import csv

from randomiser.core.enums import RunStatus
from randomiser.modes.batch_mode import run_batch
from randomiser.sources import CPUJitterSource, SchedulerJitterSource


def test_batch_mode_generates_100_seeds_and_saves_rows(tmp_path) -> None:
    sources = [
        CPUJitterSource(iterations=512),
        SchedulerJitterSource(thread_count=2, samples_per_thread=128),
    ]

    results = run_batch(
        sources,
        experiments_root=tmp_path,
        experiment_id="exp_100",
        run_count=100,
        config_name="integration",
        min_required_sources=2,
    )

    assert len(results) == 100
    assert all(result.status is RunStatus.OK for result in results)
    assert all(len(result.seed_hex) == 128 for result in results)

    output_path = tmp_path / "exp_100" / "output" / "run_index.csv"
    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 100
    assert rows[0]["run_id"] == "run_000001"
    assert rows[-1]["run_id"] == "run_000100"
    assert (tmp_path / "exp_100" / "input" / "cpu_jitter" / "run_000100.bin").exists()
    assert (tmp_path / "exp_100" / "input" / "scheduler_jitter" / "run_000100.bin").exists()


def test_batch_mode_can_generate_selected_output_for_each_seed(tmp_path) -> None:
    sources = [
        CPUJitterSource(iterations=64),
        SchedulerJitterSource(thread_count=2, samples_per_thread=16),
    ]

    results = run_batch(
        sources,
        experiments_root=tmp_path,
        experiment_id="exp_maps",
        run_count=2,
        config_name="integration",
        min_required_sources=1,
        output_kind="map",
    )

    assert len(results) == 2
    assert (tmp_path / "exp_maps" / "output" / "generated" / "map" / "run_000001.json").exists()
    assert (tmp_path / "exp_maps" / "output" / "generated" / "map" / "run_000002.json").exists()
