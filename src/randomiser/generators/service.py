from __future__ import annotations

from typing import Any

from randomiser.generators.maze import generate_maze
from randomiser.generators.otp import generate_otp
from randomiser.generators.seed_derivation import parse_master_seed
from randomiser.generators.terrain_map import generate_terrain_map

OUTPUT_KINDS = {"otp", "map", "maze"}


def generate_output(seed_hex: str, kind: str) -> dict[str, Any]:
    parse_master_seed(seed_hex)
    normalized = kind.lower()
    if normalized == "otp":
        return generate_otp(seed_hex)
    if normalized == "map":
        return generate_terrain_map(seed_hex)
    if normalized == "maze":
        return generate_maze(seed_hex)
    raise ValueError(f"unsupported output kind: {kind}")
