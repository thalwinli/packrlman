# Test Structure

### pytest as the test runner
Tests run with `pytest` using default discovery (tests/ directory, `test_*.py` files, `test_*` functions). No `pytest.ini` / `pyproject.toml` config exists — do not add one without a reason.

```bash
pytest                                             # full suite
pytest tests/test_game.py::test_step_basic         # single test
```

### Function-based tests with descriptive names
Tests are plain module-level functions (not classes) named `test_<behavior>` where the behavior part reads like a sentence — long is fine when it aids clarity.

```python
def test_ghost_collision_sets_lost_and_negative_reward():
    ...
```

### Test files mirror source modules
Each source module has a corresponding `tests/test_<module>.py`. Cross-cutting scenarios go in `tests/test_integration.py`.

*Source: 4/4 test files; CLAUDE.md command reference.*
