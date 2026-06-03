from __future__ import annotations

import csv
from pathlib import Path


def append_csv_row(path: str | Path, fieldnames: list[str], row: dict[str, str]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    should_write_header = not csv_path.exists() or csv_path.stat().st_size == 0

    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if should_write_header:
            writer.writeheader()
        writer.writerow(row)
