from __future__ import annotations

from pathlib import Path

import pytest

from randomiser.core.config_loader import load_config, validate_config
from randomiser.core.exceptions import ConfigError


def test_load_config_reads_sample_yaml_fixture() -> None:
    config_path = Path("tests/fixtures/sample_config.yaml")

    config = load_config(config_path)

    assert config["mode"] == "batch"
    assert config["experiment"]["base_dir"] == "data/experiments"
    assert config["sources"]["enabled"] == ["cpu_jitter", "scheduler_jitter"]


def test_validate_config_rejects_missing_required_sections() -> None:
    with pytest.raises(ConfigError, match="Missing required config section: sources"):
        validate_config({"mode": "batch", "experiment": {"base_dir": "data/experiments"}})


def test_validate_config_returns_config_for_valid_shape() -> None:
    config = validate_config(
        {
            "mode": "web",
            "experiment": {"base_dir": "data/experiments"},
            "sources": {"enabled": ["camera", "microphone"]},
        }
    )

    assert config["mode"] == "web"
    assert config["sources"]["enabled"] == ["camera", "microphone"]
