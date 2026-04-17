"""Gymnasium wrapper around PacmanGame for RL training.

This module is the RL bridge. Like pygame_app.py it is allowed to import
its own heavy dependency (gymnasium); the headless core in game.core /
game.map_gen / game.types remains pygame-free and gymnasium-free.
"""
from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from game.core import PacmanGame
from game.types import Action


class PacmanEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        width: int = 20,
        height: int = 15,
        wall_density: float = 0.25,
        num_ghosts: int = 3,
        seed: int | None = None,
    ):
        super().__init__()
        self._cfg = dict(
            width=width,
            height=height,
            wall_density=wall_density,
            num_ghosts=num_ghosts,
        )
        self._game = PacmanGame(seed=seed, **self._cfg)

        self.action_space = spaces.Discrete(len(Action))
        self.observation_space = spaces.Box(
            low=0.0,
            high=float(num_ghosts),
            shape=(4, height, width),
            dtype=np.float32,
        )

    def reset(self, *, seed: int | None = None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            # Fresh PacmanGame so its internal _rng is reseeded deterministically.
            self._game = PacmanGame(seed=seed, **self._cfg)
        else:
            # Advances the persistent _rng -> a fresh map per episode.
            self._game.reset()
        return self._game.to_tensor(), {}

    def step(self, action: int):
        _, reward, done = self._game.step(Action(int(action)))
        return self._game.to_tensor(), float(reward), bool(done), False, {}
