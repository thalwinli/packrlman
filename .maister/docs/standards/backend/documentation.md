# Documentation Conventions

### Module-level docstrings describe purpose and invariants
Every module opens with a triple-quoted docstring stating its purpose and any architectural invariants (e.g., "MUST NOT import pygame"). This is where load-bearing layering rules live.

```python
"""Core game logic and state management for the Pacman game.

Headless, deterministic game state and rules engine. MUST NOT import pygame.
"""
```

### CLI scripts document usage in the module docstring
Runnable entry-point scripts include a `Usage:` block in their module docstring showing how to invoke them.

```python
"""Train a PPO agent on PacmanEnv.

Usage:
    python -m rl.train_ppo [--timesteps 500000] [--n-envs 8]
"""
```

### Selective docstrings on public API
Public classes and non-trivial public methods carry docstrings. Trivial accessors and private helpers usually omit them — do not add noise.

*Source: Observed in 12/13 source modules; all 3 rl/ CLI scripts.*
