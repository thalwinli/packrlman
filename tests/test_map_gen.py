"""Tests for game.map_gen — random map generation with BFS connectivity."""
import random
from collections import deque

from game.map_gen import (
    generate_map,
    MIN_SPAWN_DIST,
    MIN_SPAWN_DIST_FLOOR,
    _bfs_distances,
    _manhattan,
)


def _bfs_reachable(start, walls, width, height):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and (nx, ny) not in walls
                and (nx, ny) not in seen
            ):
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


def test_border_walls_always_present():
    for width, height in [(10, 10), (15, 12), (20, 20), (8, 14)]:
        rng = random.Random(42)
        walls, dots, player, ghosts = generate_map(
            width=width, height=height, wall_density=0.25, num_ghosts=3, rng=rng
        )
        for x in range(width):
            assert (x, 0) in walls, f"missing top border at ({x},0) for {width}x{height}"
            assert (x, height - 1) in walls, f"missing bottom border at ({x},{height-1})"
        for y in range(height):
            assert (0, y) in walls, f"missing left border at (0,{y})"
            assert (width - 1, y) in walls, f"missing right border at ({width-1},{y})"


def test_all_dots_reachable_from_player():
    rng = random.Random(123)
    width, height = 20, 15
    walls, dots, player, ghosts = generate_map(
        width=width, height=height, wall_density=0.25, num_ghosts=4, rng=rng
    )
    reachable = _bfs_reachable(player, walls, width, height)
    unreachable = [d for d in dots if d not in reachable]
    assert not unreachable, f"Found {len(unreachable)} unreachable dots: {unreachable[:5]}"


def test_ghost_min_spawn_distance():
    rng = random.Random(7)
    width, height = 20, 15
    walls, dots, player, ghosts = generate_map(
        width=width, height=height, wall_density=0.25, num_ghosts=4, rng=rng
    )
    dist = _bfs_distances(player, walls, width, height)
    for g in ghosts:
        d = dist.get(g)
        assert d is not None, f"Ghost at {g} not reachable from player {player}"
        assert d >= MIN_SPAWN_DIST_FLOOR, (
            f"Ghost at {g} too close to player {player}: path_dist={d} "
            f"< floor={MIN_SPAWN_DIST_FLOOR}"
        )


def test_ghost_count_matches_request():
    for num in [1, 3, 5, 8]:
        rng = random.Random(num * 11)
        walls, dots, player, ghosts = generate_map(
            width=20, height=15, wall_density=0.25, num_ghosts=num, rng=rng
        )
        assert len(ghosts) == num, f"Requested {num} ghosts, got {len(ghosts)}"


def test_seeded_generation_is_deterministic():
    rng1 = random.Random(2026)
    rng2 = random.Random(2026)
    out1 = generate_map(width=18, height=14, wall_density=0.25, num_ghosts=3, rng=rng1)
    out2 = generate_map(width=18, height=14, wall_density=0.25, num_ghosts=3, rng=rng2)
    walls1, dots1, player1, ghosts1 = out1
    walls2, dots2, player2, ghosts2 = out2
    assert walls1 == walls2
    assert dots1 == dots2
    assert player1 == player2
    assert ghosts1 == ghosts2
