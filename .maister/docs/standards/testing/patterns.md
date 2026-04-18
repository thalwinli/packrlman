# Testing Patterns

### Deterministic tests via explicit seeds
Tests that exercise game behaviour instantiate `PacmanGame` / `random.Random` with explicit integer seeds to guarantee reproducibility.

```python
game = PacmanGame(seed=42)
rng = random.Random(123)
```

### Optional dependencies guarded with `pytest.importorskip`
Tests that require optional dependencies (`gymnasium`, `stable-baselines3`) skip gracefully when the dep is not installed, using `pytest.importorskip` or an explicit `try` / `except ImportError: pytest.skip(...)`.

```python
gym = pytest.importorskip("gymnasium")
```

### White-box tests access underscore-prefixed internals
It is explicitly permitted for tests to set private state (`game._player`, `game._walls`, `game._dots`, `game._ghosts`, `env._game`) to construct scenarios. The `PacmanGame` docstring sanctions this — it is a pragmatic concession to testability and is expected.

*Source: All 4 test files follow the seed pattern; test_gym_env.py uses importorskip; test_game.py uses white-box setup.*
