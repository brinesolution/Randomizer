from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_config_dir() -> Path:
    return get_project_root() / "config"


def get_data_dir() -> Path:
    return get_project_root() / "data"


def get_experiments_dir() -> Path:
    return get_data_dir() / "experiments"
