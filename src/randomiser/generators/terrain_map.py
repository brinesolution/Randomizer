from __future__ import annotations

from typing import Any

import numpy as np

from randomiser.core.hashing import sha512_digest
from randomiser.generators.seed_derivation import derive_child_seed, expand_seed

DEFAULT_WIDTH = 48
DEFAULT_HEIGHT = 48
PALETTE = [
    {"index": 0, "name": "deep_ocean", "label": "Deep ocean", "color": "#075985"},
    {"index": 1, "name": "shallow_ocean", "label": "Shallow ocean", "color": "#38bdf8"},
    {"index": 2, "name": "beach", "label": "Beach", "color": "#e7d3a1"},
    {"index": 3, "name": "land", "label": "Land", "color": "#65a30d"},
    {"index": 4, "name": "highland", "label": "Highland", "color": "#166534"},
]


def _smooth(values: np.ndarray, rounds: int = 6) -> np.ndarray:
    current = values
    for _ in range(rounds):
        padded = np.pad(current, 1, mode="edge")
        current = sum(
            padded[row:row + current.shape[0], column:column + current.shape[1]]
            for row in range(3)
            for column in range(3)
        ) / 9.0
    return current


def generate_terrain_map(
    seed_hex: str,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> dict[str, Any]:
    if width < 5 or height < 5:
        raise ValueError("map dimensions must be at least 5 by 5")
    child_seed = derive_child_seed(seed_hex, "map")
    raw = expand_seed(child_seed, width * height, namespace="terrain")
    elevation = np.frombuffer(raw, dtype=np.uint8).reshape(height, width).astype(np.float64)
    elevation = _smooth(elevation)
    thresholds = np.quantile(elevation, [0.28, 0.42, 0.54, 0.84])
    cells = np.digitize(elevation, thresholds, right=True).astype(int)
    return {
        "kind": "map",
        "width": width,
        "height": height,
        "palette": PALETTE,
        "cells": cells.tolist(),
        "childSeedHash": sha512_digest(child_seed).hex(),
    }
