"""Tests for game.core — core game logic with atomic step semantics."""
import numpy as np

from game.core import PacmanGame
from game.types import Action, Status


def test_reset_returns_state_dict_with_expected_keys():
    game = PacmanGame(seed=42)
    state = game.reset()
    expected = {"width", "height", "walls", "dots", "player", "ghosts", "score", "status", "tick"}
    assert expected.issubset(set(state.keys())), f"missing keys: {expected - set(state.keys())}"
    assert state["score"] == 0
    assert state["tick"] == 0
    assert state["status"] == "playing"


def test_step_returns_tuple_state_reward_done():
    game = PacmanGame(seed=42)
    result = game.step(Action.NOOP)
    assert isinstance(result, tuple) and len(result) == 3
    state, reward, done = result
    assert isinstance(state, dict)
    assert isinstance(reward, float)
    assert isinstance(done, bool)


def test_wall_blocks_player_movement():
    game = PacmanGame(seed=42)
    game.reset()
    # Place player at (1,1) and force a wall at (2,1). Clear ghosts far away.
    game._player = (1, 1)
    game._walls.add((2, 1))
    game._dots.discard((1, 1))
    game._dots.discard((2, 1))
    game._ghosts = [(game._width - 2, game._height - 2)]
    state, reward, done = game.step(Action.RIGHT)
    assert state["player"] == (1, 1), "player should not have moved into wall"


def test_dot_collection_increments_score_and_removes_dot():
    game = PacmanGame(seed=42)
    game.reset()
    # Put player at (1,1), ensure (2,1) is not a wall, is a dot, ghosts far.
    game._player = (1, 1)
    game._walls.discard((2, 1))
    game._walls.discard((1, 1))
    game._dots.add((2, 1))
    game._dots.discard((1, 1))
    # Remove all other dots except (2,1) would trigger win; keep at least one other
    # Ensure there's another dot so we don't immediately win
    other_dot = None
    for x in range(1, game._width - 1):
        for y in range(1, game._height - 1):
            if (x, y) != (2, 1) and (x, y) not in game._walls:
                other_dot = (x, y)
                break
        if other_dot:
            break
    game._dots.add(other_dot)
    game._ghosts = [(game._width - 2, game._height - 2)]
    prev_score = game._score
    state, reward, done = game.step(Action.RIGHT)
    assert state["player"] == (2, 1)
    assert state["score"] == prev_score + 1
    assert (2, 1) not in state["dots"]
    assert reward >= 1.0 - 0.02  # +1.0 - 0.01 time penalty


def test_ghost_collision_sets_lost_and_negative_reward():
    game = PacmanGame(seed=42)
    game.reset()
    # Force a ghost onto player's cell -> collision immediately on step.
    # Surround the cell with walls so ghost has no legal moves and stays.
    px, py = game._player
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        game._walls.add((px + dx, py + dy))
    game._dots.discard(game._player)
    game._ghosts = [game._player]
    state, reward, done = game.step(Action.NOOP)
    assert state["status"] == "lost"
    assert done is True
    assert reward <= -10.0


def test_all_dots_collected_sets_won():
    game = PacmanGame(seed=42)
    game.reset()
    # Pick a non-wall neighbor cell for the final dot
    px, py = game._player
    target = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = px + dx, py + dy
        if (nx, ny) not in game._walls and 0 <= nx < game._width and 0 <= ny < game._height:
            target = (nx, ny)
            action = {(1, 0): Action.RIGHT, (-1, 0): Action.LEFT, (0, 1): Action.DOWN, (0, -1): Action.UP}[(dx, dy)]
            break
    assert target is not None
    game._dots = {target}
    # Move ghosts far away so they don't land on player
    game._ghosts = [(game._width - 2, game._height - 2)]
    state, reward, done = game.step(action)
    assert state["status"] == "won"
    assert done is True
    assert reward >= 10.0  # +10 terminal bonus (plus +1 dot minus 0.01)


def test_to_tensor_shape_is_4_H_W():
    game = PacmanGame(width=20, height=15, seed=42)
    tensor = game.to_tensor()
    assert isinstance(tensor, np.ndarray)
    assert tensor.shape == (4, 15, 20)
