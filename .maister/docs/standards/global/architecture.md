# Global Architecture Standards

### Headless core / presentation shell split
The code is organized in strict layers. `game/types.py`, `game/map_gen.py`, and `game/core.py` form the **headless core** and MUST NOT import pygame. `game/pygame_app.py` is the **only** module permitted to import pygame, and its imports happen lazily inside `run()` so the core stays importable without pygame installed. RL bridge (`game/gym_env.py`, `rl/*`) sits between the two. This invariant is load-bearing — tests and RL training rely on it to run headlessly.
*Source: CLAUDE.md (documented); test_core_imports_without_pygame enforces it.*

### Lazy imports for heavy / optional dependencies
Heavy or optional dependencies (pygame, torch, stable_baselines3, gymnasium from entry points) are imported lazily inside the function that uses them, not at module scope. Keeps module import side-effect-free and lets the core stay usable without those dependencies installed.
*Source: Observed in all 4 entry-point modules — pygame_app.run(), rl/train_ppo.main(), rl/eval.main(), rl/play.main().*

```python
def run() -> None:
    import pygame
    from game.core import PacmanGame
    ...
```

### Deterministic seeded RNG
Determinism flows from a single `random.Random(seed)` owned by `PacmanGame` and threaded into `generate_map`. Do not introduce independent RNG sources (`random.random()`, `numpy.random` without seed, etc.) — it breaks reproducibility and silently invalidates RL training.
*Source: CLAUDE.md invariant; confirmed across game/core.py and game/map_gen.py.*
