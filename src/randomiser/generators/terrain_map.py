from __future__ import annotations

from typing import Any

import numpy as np

from randomiser.core.hashing import sha512_digest
from randomiser.generators.seed_derivation import derive_child_seed, expand_seed

DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
PALETTE = [
    {"index": 0, "name": "deep_ocean", "label": "Deep ocean", "color": "#075985"},
    {"index": 1, "name": "shallow_ocean", "label": "Shallow ocean", "color": "#38bdf8"},
    {"index": 2, "name": "beach", "label": "Beach", "color": "#e7d3a1"},
    {"index": 3, "name": "land", "label": "Land", "color": "#65a30d"},
    {"index": 4, "name": "highland", "label": "Highland", "color": "#166534"},
]


def _resize_bilinear(values: np.ndarray, width: int, height: int) -> np.ndarray:
    source_height, source_width = values.shape
    x_positions = np.linspace(0, source_width - 1, width)
    x_left = np.floor(x_positions).astype(int)
    x_right = np.minimum(x_left + 1, source_width - 1)
    x_weight = x_positions - x_left
    horizontal = (
        values[:, x_left] * (1.0 - x_weight)
        + values[:, x_right] * x_weight
    )

    y_positions = np.linspace(0, source_height - 1, height)
    y_top = np.floor(y_positions).astype(int)
    y_bottom = np.minimum(y_top + 1, source_height - 1)
    y_weight = (y_positions - y_top)[:, np.newaxis]
    return horizontal[y_top] * (1.0 - y_weight) + horizontal[y_bottom] * y_weight


def _noise_layer(
    seed: bytes,
    *,
    width: int,
    height: int,
    divisor: int,
    namespace: str,
) -> np.ndarray:
    layer_width = min(width, max(2, width // divisor))
    layer_height = min(height, max(2, height // divisor))
    raw = expand_seed(seed, layer_width * layer_height, namespace=namespace)
    values = np.frombuffer(raw, dtype=np.uint8).reshape(layer_height, layer_width).astype(np.float64)
    return _resize_bilinear(values, width, height)


def generate_terrain_map(
    seed_hex: str,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> dict[str, Any]:
    if width < 5 or height < 5:
        raise ValueError("map dimensions must be at least 5 by 5")
    child_seed = derive_child_seed(seed_hex, "map")
    elevation = (
        _noise_layer(
            child_seed,
            width=width,
            height=height,
            divisor=64,
            namespace="terrain-large",
        )
        * 0.58
        + _noise_layer(
            child_seed,
            width=width,
            height=height,
            divisor=16,
            namespace="terrain-medium",
        )
        * 0.30
        + _noise_layer(
            child_seed,
            width=width,
            height=height,
            divisor=4,
            namespace="terrain-detail",
        )
        * 0.12
    )
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
