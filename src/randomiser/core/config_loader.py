from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from randomiser.core.exceptions import ConfigError
from randomiser.core.paths import get_config_dir


REQUIRED_CONFIG_SECTIONS = ("mode", "experiment", "sources")


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = Path(path)
    if not config_path.exists():
        named_path = get_config_dir() / Path(path)
        if named_path.exists():
            config_path = named_path
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    if not isinstance(payload, dict):
        raise ConfigError("Config root must be a mapping")
    return validate_config(payload)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    for section in REQUIRED_CONFIG_SECTIONS:
        if section not in config:
            raise ConfigError(f"Missing required config section: {section}")

    enabled_sources = config["sources"].get("enabled")
    if not isinstance(enabled_sources, list) or not enabled_sources:
        raise ConfigError("Config section 'sources.enabled' must be a non-empty list")

    experiment = config["experiment"]
    if "base_dir" not in experiment:
        raise ConfigError("Config section 'experiment.base_dir' is required")

    return config
