from __future__ import annotations

from randomiser.generators.maze import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    generate_maze,
)
from randomiser.generators.seed_derivation import derive_child_seed
from randomiser.generators.service import generate_output
from randomiser.generators.terrain_map import generate_terrain_map
from randomiser.io.generated_output_store import save_generated_output


MASTER_SEED = bytes(range(64)).hex()


def test_child_seeds_are_deterministic_and_domain_separated() -> None:
    assert derive_child_seed(MASTER_SEED, "map") == derive_child_seed(MASTER_SEED, "map")
    assert derive_child_seed(MASTER_SEED, "map") != derive_child_seed(MASTER_SEED, "maze")


def test_terrain_map_is_deterministic_and_uses_five_declared_categories() -> None:
    first = generate_terrain_map(MASTER_SEED)
    second = generate_terrain_map(MASTER_SEED)

    assert first == second
    assert first["width"] == 48
    assert first["height"] == 48
    assert len(first["palette"]) == 5
    assert {item["name"] for item in first["palette"]} == {
        "deep_ocean",
        "shallow_ocean",
        "beach",
        "land",
        "highland",
    }
    assert {cell for row in first["cells"] for cell in row} == {0, 1, 2, 3, 4}


def test_maze_is_fixed_connected_perfect_and_has_closed_outer_boundary() -> None:
    maze = generate_maze(MASTER_SEED)
    cells = maze["cells"]
    size = 30

    assert maze["width"] == size
    assert maze["height"] == size
    assert maze["start"] == [0, 0]
    assert maze["end"] == [size - 1, size - 1]
    assert len(cells) == size
    assert all(len(row) == size for row in cells)
    assert all(cells[0][column] & NORTH for column in range(size))
    assert all(cells[size - 1][column] & SOUTH for column in range(size))
    assert all(cells[row][0] & WEST for row in range(size))
    assert all(cells[row][size - 1] & EAST for row in range(size))

    open_edges = 0
    visited = {(0, 0)}
    pending = [(0, 0)]
    while pending:
        row, column = pending.pop()
        for wall, opposite, row_delta, column_delta in [
            (NORTH, SOUTH, -1, 0),
            (EAST, WEST, 0, 1),
            (SOUTH, NORTH, 1, 0),
            (WEST, EAST, 0, -1),
        ]:
            next_row = row + row_delta
            next_column = column + column_delta
            if not (0 <= next_row < size and 0 <= next_column < size):
                continue
            assert bool(cells[row][column] & wall) == bool(cells[next_row][next_column] & opposite)
            if not cells[row][column] & wall:
                if wall in {EAST, SOUTH}:
                    open_edges += 1
                if (next_row, next_column) not in visited:
                    visited.add((next_row, next_column))
                    pending.append((next_row, next_column))

    assert len(visited) == size * size
    assert open_edges == size * size - 1


def test_service_generates_each_selectable_output() -> None:
    otp = generate_output(MASTER_SEED, "otp")
    terrain_map = generate_output(MASTER_SEED, "map")
    maze = generate_output(MASTER_SEED, "maze")

    assert otp["kind"] == "otp"
    assert len(otp["otp"]) == 6
    assert terrain_map["kind"] == "map"
    assert maze["kind"] == "maze"


def test_generated_output_store_saves_selected_output(tmp_path) -> None:
    output = generate_output(MASTER_SEED, "map")

    path = save_generated_output(tmp_path, "run_000001", output)

    assert path == tmp_path / "output" / "generated" / "map" / "run_000001.json"
    assert path.exists()
