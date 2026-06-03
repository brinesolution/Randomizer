"""Run the Randomiser local web app."""
from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    subprocess.run(["node", "apps/web/server.js"], cwd=project_root, check=True)


if __name__ == "__main__":
    main()
