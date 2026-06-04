from __future__ import annotations

import random
from typing import Any

from randomiser.core.hashing import sha512_digest
from randomiser.generators.seed_derivation import derive_child_seed

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST
SIZE = 30

DIRECTIONS = [
    (NORTH, SOUTH, -1, 0),
    (EAST, WEST, 0, 1),
    (SOUTH, NORTH, 1, 0),
    (WEST, EAST, 0, -1),
]


def generate_maze(seed_hex: str) -> dict[str, Any]:
    child_seed = derive_child_seed(seed_hex, "maze")
    rng = random.Random(int.from_bytes(child_seed, "big"))
    cells = [[ALL_WALLS for _ in range(SIZE)] for _ in range(SIZE)]
    visited = {(0, 0)}
    stack = [(0, 0)]

    while stack:
        row, column = stack[-1]
        candidates = []
        for wall, opposite, row_delta, column_delta in DIRECTIONS:
            next_row = row + row_delta
            next_column = column + column_delta
            if 0 <= next_row < SIZE and 0 <= next_column < SIZE and (next_row, next_column) not in visited:
                candidates.append((wall, opposite, next_row, next_column))
        if not candidates:
            stack.pop()
            continue
        wall, opposite, next_row, next_column = rng.choice(candidates)
        cells[row][column] &= ~wall
        cells[next_row][next_column] &= ~opposite
        visited.add((next_row, next_column))
        stack.append((next_row, next_column))

    return {
        "kind": "maze",
        "width": SIZE,
        "height": SIZE,
        "cells": cells,
        "start": [0, 0],
        "end": [SIZE - 1, SIZE - 1],
        "wallBits": {"north": NORTH, "east": EAST, "south": SOUTH, "west": WEST},
        "childSeedHash": sha512_digest(child_seed).hex(),
    }
