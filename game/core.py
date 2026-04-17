"""Core game logic and state management for the Pacman game.

Headless, deterministic game state and rules engine. MUST NOT import pygame.
"""
import random

import numpy as np

from game.map_gen import generate_map
from game.types import Action, Status


# Action -> (dx, dy) delta
_ACTION_DELTA = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
    Action.NOOP: (0, 0),
}

TIME_PENALTY = 0.01
DOT_REWARD = 1.0
WIN_BONUS = 10.0
LOSS_PENALTY = 10.0

GHOST_TURN_PROB = 0.2


class PacmanGame:
    """Headless Pacman game with atomic step semantics.

    Attributes (internal, subject to change but used by tests):
        _width, _height: board dimensions
        _walls: set[(x,y)]
        _dots: set[(x,y)]
        _player: (x,y)
        _ghosts: list[(x,y)]
        _score: int
        _tick: int
        _status: Status
        _rng: random.Random
    """

    def __init__(self, width=20, height=15, wall_density=0.25, num_ghosts=3, seed=None):
        self._width = width
        self._height = height
        self._wall_density = wall_density
        self._num_ghosts = num_ghosts
        self._rng = random.Random(seed)
        self.reset()

    # ------------------------------------------------------------------ public
    def reset(self):
        walls, dots, player_pos, ghost_positions = generate_map(
            width=self._width,
            height=self._height,
            wall_density=self._wall_density,
            num_ghosts=self._num_ghosts,
            rng=self._rng,
        )
        self._walls = set(walls)
        self._dots = set(dots)
        self._player = player_pos
        self._ghosts = list(ghost_positions)
        self._ghost_dirs = [self._pick_initial_dir(g) for g in self._ghosts]
        self._score = 0
        self._tick = 0
        self._status = Status.PLAYING
        return self.get_state()

    def step(self, action):
        """Advance one tick. Returns (state_dict, reward, done)."""
        if self._status is not Status.PLAYING:
            # Terminal state: idempotent return
            return self.get_state(), 0.0, True

        reward = 0.0

        # 1) Player move
        dx, dy = _ACTION_DELTA[action]
        px, py = self._player
        tx, ty = px + dx, py + dy
        if self._is_passable(tx, ty):
            self._player = (tx, ty)

        # 2) Dot collection
        if self._player in self._dots:
            self._dots.remove(self._player)
            self._score += 1
            reward += DOT_REWARD

        # 3) Ghost moves: keep heading until blocked, then pick a passable direction
        if len(self._ghost_dirs) != len(self._ghosts):
            self._ghost_dirs = [self._pick_initial_dir(g) for g in self._ghosts]
        new_ghosts = []
        new_dirs = []
        for (gx, gy), (ddx, ddy) in zip(self._ghosts, self._ghost_dirs):
            options = [
                (odx, ody)
                for odx, ody in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if self._is_passable(gx + odx, gy + ody)
            ]
            current_ok = self._is_passable(gx + ddx, gy + ddy)
            if current_ok and self._rng.random() >= GHOST_TURN_PROB:
                nd = (ddx, ddy)
            elif options:
                nd = self._rng.choice(options)
            else:
                new_ghosts.append((gx, gy))
                new_dirs.append((ddx, ddy))
                continue
            new_ghosts.append((gx + nd[0], gy + nd[1]))
            new_dirs.append(nd)
        self._ghosts = new_ghosts
        self._ghost_dirs = new_dirs

        # 4) Collision check
        done = False
        if any(g == self._player for g in self._ghosts):
            self._status = Status.LOST
            reward -= LOSS_PENALTY
            done = True
        elif not self._dots:
            # 5) All dots collected -> win
            self._status = Status.WON
            reward += WIN_BONUS
            done = True
        else:
            # 6) Time penalty
            reward -= TIME_PENALTY

        self._tick += 1
        return self.get_state(), float(reward), done

    def get_state(self):
        return {
            "width": self._width,
            "height": self._height,
            "walls": set(self._walls),
            "dots": set(self._dots),
            "player": self._player,
            "ghosts": list(self._ghosts),
            "score": self._score,
            "status": self._status.value,
            "tick": self._tick,
        }

    def to_tensor(self):
        """Encode state as numpy array shape (4, height, width).

        Channels: 0=walls, 1=dots, 2=player, 3=ghosts.
        Multiple ghosts on the same cell are summed (not clipped) so overlap is visible.
        """
        H, W = self._height, self._width
        t = np.zeros((4, H, W), dtype=np.float32)
        for x, y in self._walls:
            t[0, y, x] = 1.0
        for x, y in self._dots:
            t[1, y, x] = 1.0
        px, py = self._player
        t[2, py, px] = 1.0
        for gx, gy in self._ghosts:
            t[3, gy, gx] += 1.0  # sum overlap
        return t

    # ----------------------------------------------------------------- helpers
    def _pick_initial_dir(self, ghost_pos):
        gx, gy = ghost_pos
        options = [
            (dx, dy)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if self._is_passable(gx + dx, gy + dy)
        ]
        return self._rng.choice(options) if options else (0, 0)

    def _is_passable(self, x, y):
        if not (0 <= x < self._width and 0 <= y < self._height):
            return False
        if (x, y) in self._walls:
            return False
        return True
