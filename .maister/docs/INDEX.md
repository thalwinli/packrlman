# Documentation Index

**IMPORTANT**: Read this file at the beginning of any development task to understand available documentation and standards.

## Quick Reference

### Project Documentation
Project-level documentation covering technology choices and system architecture for **packrlman** — a Pacman RL environment with a headless-core / presentation-shell split.

### Technical Standards
Coding standards, conventions, and best practices organized by domain (global, backend, testing). Frontend is not initialized for this project.

---

## Project Documentation

Located in `.maister/docs/project/`

### Tech Stack (`project/tech-stack.md`)
Technology choices and rationale: Python 3.10+, Pygame (presentation shell only, lazy-imported), custom headless game engine + NumPy, Gymnasium wrapper, Stable-Baselines3 PPO with a `SmallCNN` feature extractor, PyTorch, TensorBoard, and pytest. Lists key dependencies, entry points (`main.py`, `rl.train_ppo`, `rl.eval`, `rl.play`, `pytest`), and notes the absence of a database, CI/CD, linter, and type-checker.

### Architecture (`project/architecture.md`)
System architecture as three concentric layers: (1) headless core in `game/types.py`, `game/core.py`, `game/map_gen.py` (deterministic rules, BFS-verified map generation, reward constants), (2) presentation shell in `game/pygame_app.py` (the only module permitted to import pygame, lazy imports, 60 FPS render / 150 ms tick), and (3) RL bridge via `game/gym_env.py` + `rl/` scripts. Documents the "no pygame in core" invariant, tick order within `step()`, data flow from input to policy, testing strategy, and key risks.

---

## Technical Standards

### Global Standards

Located in `.maister/docs/standards/global/`

#### Architecture (`standards/global/architecture.md`)
Headless core / presentation shell split (pygame isolated to `game/pygame_app.py`), lazy imports for heavy/optional dependencies (pygame, torch, stable_baselines3), and deterministic seeded RNG threaded through `PacmanGame` and `generate_map`.

#### Naming (`standards/global/naming.md`)
File names in `snake_case`, test files mirror source as `test_<module>.py`, PascalCase classes, snake_case functions/methods, UPPER_SNAKE_CASE module-level constants at the top of the file, and underscore-prefixed private members (explicitly accessible from tests).

#### Version Control (`standards/global/vcs.md`)
`.gitignore` scope: Python bytecode, pytest/coverage caches, virtualenvs, IDE folders, RL training artifacts (`ppo_pacman*.zip`, `*.zip`, `tb/`, `runs/`), and per-user Claude Code settings (`.claude/settings.local.json`).

#### Coding Style (`standards/global/coding-style.md`)
Naming consistency, automatic formatting, descriptive names, focused functions, uniform indentation, no dead code, no backward compatibility unless required, and DRY.

#### Commenting (`standards/global/commenting.md`)
Let code speak for itself, comment sparingly, and never leave change-log comments in source.

#### Conventions (`standards/global/conventions.md`)
Predictable project structure, up-to-date documentation, clean version control, environment variables for config, minimal dependencies, consistent code reviews, testing standards, feature flags, changelog updates, and build-what's-needed discipline.

#### Error Handling (`standards/global/error-handling.md`)
Clear user-facing messages, fail-fast on invalid state, typed exceptions, centralized handling, graceful degradation, retry with backoff, and explicit resource cleanup.

#### Minimal Implementation (`standards/global/minimal-implementation.md`)
Build only what you need, clear purpose per module, delete exploration artifacts, no future stubs, no speculative abstractions, review before commit, and treat unused code as debt.

#### Validation (`standards/global/validation.md`)
Server-side validation always, client-side for feedback only, validate early, return specific errors, allowlists over blocklists, type/format checks, input sanitization, business-rule validation, and consistent enforcement across entry points.

### Backend Standards

Located in `.maister/docs/standards/backend/`

#### Imports (`standards/backend/imports.md`)
Absolute imports from the package root (`game.`, `rl.`) — no relative imports — and PEP 8 import grouping (stdlib / third-party / local, separated by blank lines).

#### Documentation (`standards/backend/documentation.md`)
Module-level docstrings state purpose and architectural invariants, CLI entry-point scripts include a `Usage:` block in their module docstring, and docstrings are selective (public API yes, trivial accessors no).

#### Module Structure (`standards/backend/structure.md`)
Module-level constants appear at the top of the file (after imports), and runnable scripts define a `main()` function guarded by `if __name__ == "__main__": main()` — argparse lives inside `main()`.

#### Game Engine Contracts (`standards/backend/game-contracts.md`)
Load-bearing semantics of `PacmanGame`: atomic `step(action)` with fixed tick order (player move → dot collect → ghost moves → collision → win → time penalty), idempotent terminal steps, `to_tensor()` returning a `(4, H, W)` float32 array with channels `walls, dots, player, ghosts` (ghost overlap summed), and reward constants living in `game/core.py`.

#### Map Generation (`standards/backend/map-gen.md`)
`generate_map` must produce BFS-verified reachable maps (retry with decreasing wall density, last-resort zero interior walls, raise `RuntimeError` on failure). Ghost spawn placement uses BFS path distance >= `MIN_SPAWN_DIST` (default 5), degrading down to `MIN_SPAWN_DIST_FLOOR` (2).

#### Dependencies (`standards/backend/dependencies.md`)
Split core vs. RL dependencies: `requirements.txt` (pygame, numpy) vs. `requirements-rl.txt` (gymnasium, stable-baselines3, torch, tensorboard). Core must run without RL deps. Pin minimum versions with `>=`, not `==`; no lockfile.

#### Error Handling (`standards/backend/error-handling.md`)
Project-specific: raise built-in exceptions (`RuntimeError`, `ValueError`, `ImportError`) with descriptive f-string messages. Do not introduce a custom exception hierarchy — over-engineering for a project of this size.

### Frontend Standards

*Not initialized for this project. The only "frontend" surface is `game/pygame_app.py`, which is a native desktop rendering layer rather than a web UI. If web frontend work is added later, you can:*
- *Add standards manually using the docs-manager skill*
- *Run `/maister:standards-discover --scope=frontend` to auto-discover*

### Testing Standards

Located in `.maister/docs/standards/testing/`

#### Test Structure (`standards/testing/structure.md`)
pytest with default discovery (no config file), function-based tests named `test_<behavior>` (long descriptive names welcome), and test files mirror source modules (`tests/test_<module>.py`); cross-cutting scenarios in `tests/test_integration.py`.

#### Testing Patterns (`standards/testing/patterns.md`)
Deterministic tests via explicit integer seeds (`PacmanGame(seed=42)`, `random.Random(123)`), optional dependencies guarded with `pytest.importorskip` (e.g., gymnasium, stable-baselines3), and white-box tests explicitly permitted to access underscore-prefixed internals (`game._player`, `game._walls`, etc.) for scenario setup.

#### Test Writing (`standards/testing/test-writing.md`)
Test behavior (not implementation), clear test names, mock external dependencies, fast execution, risk-based test prioritization, balance coverage with velocity, critical-path focus, and appropriate depth per test type.

---

## How to Use This Documentation

1. **Start Here**: Always read this INDEX.md first to understand what documentation exists
2. **Project Context**: Read `project/tech-stack.md` and `project/architecture.md` before non-trivial changes — the headless-core invariant is load-bearing
3. **Standards**: Reference appropriate standards under `standards/` when writing code
4. **Keep Updated**: Update documentation when making significant changes
5. **Customize**: Adapt all documentation to packrlman's specific needs

## Updating Documentation

- Project documentation should be updated when tech stack, entry points, or architecture changes (e.g., new RL algorithm, new module layer, added CI/CD)
- Technical standards should be updated when team conventions evolve — use `/maister:standards-update`
- Always update INDEX.md when adding, removing, or significantly changing documentation
