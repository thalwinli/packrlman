# Technology Stack

## Overview
This document describes the technology choices and rationale for **packrlman** — a Pacman implementation in Python designed from inception as a reinforcement learning environment, with a strict headless-core / presentation-shell split.

## Languages

### Python 3.10+
- **Usage**: 100% of codebase (~16 Python modules)
- **Rationale**: Dominant language in the RL/ML ecosystem (PyTorch, gymnasium, stable-baselines3). Enables a single language across game logic, training, and presentation.
- **Key Features Used**: `from __future__ import annotations`, type hints, `Enum`, dataclasses, f-strings, modern typing constructs.

## Frameworks

### Frontend / Presentation
- **Pygame** (`>=2.5`) — Interactive rendering and input handling. Only `game/pygame_app.py` imports pygame, and it does so lazily inside `run()` so the core stays importable without pygame installed.

### Backend / Core
- **Custom headless game engine** (`game/core.py`) — Deterministic rules engine with atomic `step(action) -> (state, reward, done)` semantics. Pure Python + NumPy only; no pygame.
- **Procedural map generator** (`game/map_gen.py`) — BFS-verified connectivity; BFS path distance for ghost spawn placement with graceful degradation of wall density.

### RL / ML
- **Gymnasium** (`>=0.29`) — Modern `gym` successor. `game/gym_env.py` wraps `PacmanGame` in a `gymnasium.Env` with `Discrete(5)` actions and a `Box(4, 15, 20)` float32 observation space (walls / dots / player / ghosts channels).
- **Stable-Baselines3** (`>=2.3`) — PPO training pipeline in `rl/train_ppo.py` with a custom `SmallCNN` feature extractor.
- **PyTorch** (`>=2.2`) — Backend for the CNN feature extractor.
- **TensorBoard** (`>=2.15`) — Training visualization (logs under `./tb/`).

### Testing
- **pytest** — Unit and integration tests under `tests/`. No config file (pytest defaults). Tests exercise the headless core so they run without pygame.

## Database
Not applicable — packrlman is an offline single-process game + RL environment with no persistence layer beyond Stable-Baselines3 model checkpoints (`.zip`).

## Build Tools & Package Management
- **pip** with `requirements.txt` (core) and `requirements-rl.txt` (RL extras).
- No lockfile / no virtualenv manager checked in.

## Infrastructure

### Containerization
Not used.

### CI/CD
Not configured. See `.maister/docs/project/architecture.md` — opportunity noted.

### Hosting
Not applicable (local/desktop project).

## Development Tools

### Linting & Formatting
Not configured. Style is enforced by convention only.

### Type Checking
Type hints present throughout but not validated (no mypy config).

## Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| pygame | >=2.5 | Presentation shell (rendering, input) |
| numpy | >=1.24 | Tensor encoding (`to_tensor`) and array ops |
| gymnasium | >=0.29 | RL environment API |
| stable-baselines3 | >=2.3 | PPO training |
| torch | >=2.2 | CNN feature extractor backend |
| tensorboard | >=2.15 | Training metric logging |
| pytest | * | Testing |

## Version Management
Versions pinned with `>=` in requirements files. No lockfile.

## Entry Points
- `python main.py` — GUI game via `game.pygame_app.run()`
- `python -m rl.train_ppo` — PPO training
- `python -m rl.eval` — Evaluate a trained model
- `python -m rl.play` — Watch a trained agent in the pygame window
- `pytest` — Run tests

---
*Last Updated*: 2026-04-18
*Auto-detected*: language, frameworks, dependencies, entry points, testing tool. *User-provided*: goals (RL experimentation, training, vibe-coding, portfolio).
