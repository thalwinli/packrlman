"""Procedural map generation for the Pacman game.

Generates maze layouts as pure data structures. MUST NOT import pygame.
"""
from collections import deque
from random import Random

MIN_SPAWN_DIST = 8
MIN_SPAWN_DIST_FLOOR = 5
MAX_REGEN_ATTEMPTS = 20


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _bfs_distances(start, walls, width, height):
    """Return dict of reachable cell -> path distance (4-connected, walls blocking)."""
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and (nx, ny) not in walls
                and (nx, ny) not in dist
            ):
                dist[(nx, ny)] = d + 1
                q.append((nx, ny))
    return dist


def _bfs_reachable(start, walls, width, height):
    """Return set of cells reachable from start (wraps _bfs_distances for compat)."""
    return set(_bfs_distances(start, walls, width, height).keys())


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

    # BFS path distances from player; only reachable cells are candidates.
    # Using path distance (not Manhattan) keeps ghosts genuinely far through the maze.
    dist_from_player = _bfs_distances(player_pos, walls, width, height)
    reachable_pool = [c for c in remaining if c in dist_from_player]

    ghost_positions = []
    threshold = MIN_SPAWN_DIST
    while threshold >= MIN_SPAWN_DIST_FLOOR:
        candidates = [c for c in reachable_pool if dist_from_player[c] >= threshold]
        if len(candidates) >= num_ghosts:
            ghost_positions = rng.sample(candidates, num_ghosts)
            break
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
