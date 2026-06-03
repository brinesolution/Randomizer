from __future__ import annotations

from pathlib import Path

from randomiser.core.enums import SourceName
from randomiser.core.models import OtpRunResult
from randomiser.io.artifact_namer import output_index_relative_path
from randomiser.io.csv_writer import append_csv_row

RUN_INDEX_COLUMNS = [
    "run_id",
    "mode",
    "camera_input_file",
    "microphone_input_file",
    "cpu_jitter_input_file",
    "scheduler_jitter_input_file",
    "otp",
    "status",
    "created_at",
]

SOURCE_COLUMNS = {
    SourceName.CAMERA.value: "camera_input_file",
    SourceName.MICROPHONE.value: "microphone_input_file",
    SourceName.CPU_JITTER.value: "cpu_jitter_input_file",
    SourceName.SCHEDULER_JITTER.value: "scheduler_jitter_input_file",
}


def output_row(result: OtpRunResult) -> dict[str, str]:
    row = {
        "run_id": result.run_id,
        "mode": result.mode.value,
        "camera_input_file": "",
        "microphone_input_file": "",
        "cpu_jitter_input_file": "",
        "scheduler_jitter_input_file": "",
        "otp": result.otp,
        "status": result.status.value,
        "created_at": result.created_at.isoformat() if result.created_at else "",
    }

    for source_name, column_name in SOURCE_COLUMNS.items():
        row[column_name] = result.source_files.get(source_name, "")

    return row


def append_output_row(experiment_dir: str | Path, result: OtpRunResult) -> Path:
    output_path = Path(experiment_dir) / output_index_relative_path()
    append_csv_row(output_path, RUN_INDEX_COLUMNS, output_row(result))
    return output_path
