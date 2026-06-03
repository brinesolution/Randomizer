from __future__ import annotations

import csv

import pytest

from randomiser.cli.app import main


def test_cli_help_exits_cleanly(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "run-once" in capsys.readouterr().out


def test_cli_run_once_writes_one_experiment_row(tmp_path, capsys) -> None:
    exit_code = main(
        [
            "run-once",
            "--config",
            "config/cpu_scheduler_only.yaml",
            "--experiments-root",
            str(tmp_path),
            "--experiment-id",
            "exp_cli_once",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "OTP" in output
    output_path = tmp_path / "exp_cli_once" / "output" / "run_index.csv"
    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["run_id"] == "run_000001"
    assert len(rows[0]["otp"]) == 6


def test_cli_inspect_experiment_prints_summary(tmp_path, capsys) -> None:
    main(
        [
            "run-once",
            "--config",
            "config/cpu_scheduler_only.yaml",
            "--experiments-root",
            str(tmp_path),
            "--experiment-id",
            "exp_cli_inspect",
        ]
    )

    exit_code = main(["inspect-experiment", str(tmp_path / "exp_cli_inspect")])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "exp_cli_inspect" in output
    assert "rows: 1" in output
