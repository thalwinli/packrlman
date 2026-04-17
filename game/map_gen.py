"""Procedural map generation for the Pacman game.

Generates maze layouts as pure data structures. MUST NOT import pygame.
"""
from collections import deque
from random import Random

MIN_SPAWN_DIST = 5
MAX_REGEN_ATTEMPTS = 20


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _bfs_reachable(start, walls, width, height):
    """Return set of cells reachable from start over non-wall 4-connected neighbors."""
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


def _attempt_generate(width, height, wall_density, num_ghosts, rng):
    """One attempt at generating a map. Returns tuple or None if ghost placement infeasible."""
    walls = set()
    # Border walls
    for x in range(width):
        walls.add((x, 0))
        walls.add((x, height - 1))
    for y in range(height):
        walls.add((0, y))
        walls.add((width - 1, y))
    # Interior random walls
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            if rng.random() < wall_density:
                walls.add((x, y))

    # Collect empty cells
    empties = [
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in walls
    ]
    if len(empties) < 1 + num_ghosts:
        return None

    # Pick player spawn
    player_pos = rng.choice(empties)
    remaining = [c for c in empties if c != player_pos]

    # Pick ghosts with Manhattan distance >= MIN_SPAWN_DIST, degrading down to 2
    ghost_positions = []
    threshold = MIN_SPAWN_DIST
    pool = list(remaining)
    while len(ghost_positions) < num_ghosts and threshold >= 2:
        candidates = [c for c in pool if _manhattan(player_pos, c) >= threshold]
        if len(candidates) >= (num_ghosts - len(ghost_positions)):
            # Pick needed number from candidates
            needed = num_ghosts - len(ghost_positions)
            picks = rng.sample(candidates, needed)
            ghost_positions.extend(picks)
            for p in picks:
                pool.remove(p)
            break
        else:
            threshold -= 1

    if len(ghost_positions) < num_ghosts:
        return None

    # Remaining empties become dots
    ghost_set = set(ghost_positions)
    dots = {c for c in remaining if c not in ghost_set}

    return walls, dots, player_pos, ghost_positions


def generate_map(width, height, wall_density, num_ghosts, rng):
    """Generate a random game map with BFS-verified connectivity.

    Returns:
        (walls, dots, player_pos, ghost_positions)
        - walls: set[tuple[int,int]]
        - dots: set[tuple[int,int]]
        - player_pos: tuple[int,int]
        - ghost_positions: list[tuple[int,int]]
    """
    current_density = wall_density
    while current_density >= 0.0:
        for _ in range(MAX_REGEN_ATTEMPTS):
            result = _attempt_generate(width, height, current_density, num_ghosts, rng)
            if result is None:
                continue
            walls, dots, player_pos, ghost_positions = result
            reachable = _bfs_reachable(player_pos, walls, width, height)
            if all(d in reachable for d in dots):
                return walls, dots, player_pos, ghost_positions
        # Reduce density and retry
        current_density -= 0.05
        if current_density < 0:
            break

    # Last resort: no interior walls at all
    result = _attempt_generate(width, height, 0.0, num_ghosts, rng)
    if result is None:
        raise RuntimeError(
            f"Could not generate map {width}x{height} with {num_ghosts} ghosts"
        )
    return result
