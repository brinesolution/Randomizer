from __future__ import annotations

from argparse import Namespace

from randomiser.core.config_loader import load_config
from randomiser.modes.batch_mode import build_sources_from_config
from randomiser.pipeline.calibration import calibrate_sources
from randomiser.pipeline.warmup import check_source_availability


def calibrate_command(args: Namespace) -> int:
    config = load_config(args.config)
    sources = build_sources_from_config(config)
    availability = check_source_availability(sources)
    health = calibrate_sources(sources)

    for source in sources:
        name = source.name.value
        health_status = health[name].status.value if name in health else "missing"
        print(f"{name}: available={availability.get(name, False)} health={health_status}")

    return 0
