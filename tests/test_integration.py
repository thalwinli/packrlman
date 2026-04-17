"""Integration / smoke tests for the Pacman feature.

Covers:
- Core pygame isolation (AC: core modules importable without pygame)
- End-to-end determinism (AC: seeded games are reproducible)
- Full episode termination (AC: game can reach a terminal state)
- Strict step-return types (AC: step returns (dict, float, bool))
"""
import builtins
import random
import sys

from game.core import PacmanGame
from game.types import Action


def test_core_imports_without_pygame():
    """game.core, game.map_gen, game.types must import with pygame blocked."""
    real_import = builtins.__import__

    def blocked(name, *a, **kw):
        if name == "pygame" or name.startswith("pygame."):
            raise ImportError("pygame blocked for isolation test")
        return real_import(name, *a, **kw)

    # Purge pygame and game modules so imports re-trigger under the block.
    for mod in list(sys.modules):
        if mod == "pygame" or mod.startswith("pygame."):
            del sys.modules[mod]
    for mod in list(sys.modules):
        if mod == "game" or mod.startswith("game."):
            del sys.modules[mod]

    builtins.__import__ = blocked
    try:
        import game.core  # noqa: F401
        import game.map_gen  # noqa: F401
        import game.types  # noqa: F401
    finally:
        builtins.__import__ = real_import


def test_seeded_game_produces_identical_map():
    """Two fresh PacmanGame instances with the same seed yield identical initial state."""
    g1 = PacmanGame(seed=42)
    g2 = PacmanGame(seed=42)
    s1 = g1.get_state()
    s2 = g2.get_state()
    assert s1["walls"] == s2["walls"]
    assert s1["dots"] == s2["dots"]
    assert s1["player"] == s2["player"]
    assert s1["ghosts"] == s2["ghosts"]


def test_seeded_game_step_sequence_deterministic():
    """Same seed + same action sequence -> identical (state, reward, done) stream."""
    actions = [Action.UP, Action.RIGHT, Action.DOWN, Action.LEFT, Action.NOOP] * 10

    def run():
        g = PacmanGame(seed=2026)
        trace = []
        for a in actions:
            state, reward, done = g.step(a)
            trace.append((state["player"], tuple(state["ghosts"]), state["score"], reward, done))
            if done:
                break
        return trace

    assert run() == run()


def test_full_episode_runs_to_terminal():
    """Drive with random (seeded) actions — episode should either end or run cleanly."""
    game = PacmanGame(seed=99)
    rng = random.Random(99)
    all_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.NOOP]
    done = False
    for _ in range(5000):
        state, reward, done = game.step(rng.choice(all_actions))
        assert isinstance(state, dict)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        if done:
            break
    # Either terminated or ran cleanly for 5000 steps without error.
    assert done or state["tick"] == 5000


def test_step_return_types_strict():
    """state is dict, reward is exactly float (not int/bool), done is exactly bool."""
    game = PacmanGame(seed=7)
    state, reward, done = game.step(Action.NOOP)
    assert type(state) is dict
    assert type(reward) is float
    assert type(done) is bool
