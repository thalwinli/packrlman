"""Smoke tests for the gymnasium wrapper.

Skipped if gymnasium is not installed.
"""
import numpy as np
import pytest

gym = pytest.importorskip("gymnasium")

from game.gym_env import PacmanEnv


def test_env_basic_api():
    env = PacmanEnv(seed=7)
    obs, info = env.reset()
    assert obs.shape == (4, 15, 20)
    assert obs.dtype == np.float32
    assert isinstance(info, dict)

    obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
    assert obs.shape == (4, 15, 20)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert truncated is False


def test_env_deterministic_with_seed():
    e1 = PacmanEnv(seed=42)
    e2 = PacmanEnv(seed=42)
    o1, _ = e1.reset(seed=42)
    o2, _ = e2.reset(seed=42)
    assert np.array_equal(o1, o2)


def test_env_varies_maps_across_resets_without_seed():
    env = PacmanEnv(seed=1)
    env.reset()
    obs_a = env._game.to_tensor().copy()
    # step a few times to advance RNG state, then reset without seed
    for _ in range(5):
        env.step(env.action_space.sample())
    env.reset()
    obs_b = env._game.to_tensor().copy()
    # Not guaranteed to differ, but overwhelmingly likely.
    assert not np.array_equal(obs_a, obs_b)


def test_env_passes_sb3_check_env_if_available():
    try:
        from stable_baselines3.common.env_checker import check_env
    except ImportError:
        pytest.skip("stable-baselines3 not installed")
    env = PacmanEnv(seed=0)
    check_env(env, warn=True)
