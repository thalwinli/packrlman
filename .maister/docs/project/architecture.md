# System Architecture

## Overview
packrlman is organized as three concentric layers around a deterministic game core:

1. **Headless core** (`game/types.py`, `game/core.py`, `game/map_gen.py`) — pure rules engine. No pygame, no gymnasium.
2. **Presentation shell** (`game/pygame_app.py`) — the only module permitted to import pygame.
3. **RL bridge** (`game/gym_env.py` + `rl/`) — gymnasium wrapper plus training / evaluation / playback scripts.

This split is load-bearing: tests, RL training, and headless CI all depend on the core being importable without pygame or a display.

## Architecture Pattern
**Pattern**: Headless Core / Presentation Shell with RL bridge.

The core exposes an atomic `step(action) -> (state, reward, done)` API and a `to_tensor() -> (4, H, W) float32` observation encoder. The presentation shell drives the core on a fixed 150 ms tick while rendering at 60 FPS. The gymnasium wrapper adapts the same core into a standard RL environment.

**Invariant**: `game/types.py`, `game/map_gen.py`, and `game/core.py` MUST NOT import pygame. Enforced by convention and documented in `CLAUDE.md`.

## System Structure

### Headless Core (`game/`)
- **Location**: `game/types.py`, `game/core.py`, `game/map_gen.py`
- **Purpose**: Deterministic game rules, state, and map generation.
- **Key files**:
  - `types.py` — `Action`, `Status` enums. Pure data.
  - `core.py` — `PacmanGame` class. Owns a single `random.Random(seed)` for determinism. Tick order: player move → dot collect → ghost moves → collision check → win check → time penalty. Terminal steps are idempotent. Reward constants (`TIME_PENALTY`, `DOT_REWARD`, `WIN_BONUS`, `LOSS_PENALTY`) live here.
  - `map_gen.py` — Procedural generator. BFS verifies every dot is reachable from the player spawn; wall density degrades on failure, falling back to no interior walls. Ghosts placed via BFS path distance (`MIN_SPAWN_DIST=5`, degrading to 2 if needed).

### Presentation Shell (`game/pygame_app.py`)
- **Location**: `game/pygame_app.py`
- **Purpose**: Interactive GUI. Renders at `FPS=60`; advances the core every `TICK_MS=150`. Between ticks, the most recent arrow-key input is buffered as `pending_action`. Redraws only on state change.
- **Constraint**: Pygame imports happen lazily inside `run()` so the core is importable without pygame installed.

### RL Bridge (`game/gym_env.py` + `rl/`)
- **Location**: `game/gym_env.py` (wrapper), `rl/train_ppo.py`, `rl/eval.py`, `rl/play.py`
- **Purpose**:
  - `gym_env.py` — `PacmanEnv(gymnasium.Env)`. `Discrete(5)` action space (UP/DOWN/LEFT/RIGHT/NOOP). `Box(4, 15, 20)` float32 observation. `reset(seed=X)` reinitializes deterministically; `reset()` uses persistent RNG.
  - `rl/train_ppo.py` — PPO training with `SmallCNN` feature extractor (Conv2d 4→16, 16→32, flatten, linear). Uses `SubprocVecEnv` for parallelism. Logs to `./tb/`.
  - `rl/eval.py` — Runs N episodes, reports mean / std return and win rate.
  - `rl/play.py` — Loads a trained model and visualizes play in the pygame window.

## Data Flow

```
Input (keyboard / policy)
        │
        ▼
Action enum ──► PacmanGame.step(action)
                    │
                    ├─► player move (wall check)
                    ├─► dot collection        ──► reward += DOT_REWARD
                    ├─► ghost moves (BFS)
                    ├─► collision check       ──► reward -= LOSS_PENALTY, done
                    ├─► win check             ──► reward += WIN_BONUS, done
                    └─► time penalty          ──► reward -= TIME_PENALTY
                    │
                    ▼
        (state_dict, reward, done)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  pygame_app.run        PacmanGame.to_tensor()
  (render grid)              (4, H, W) float32
                                  │
                                  ▼
                        gymnasium.Env.step()
                                  │
                                  ▼
                         PPO (SmallCNN policy)
```

## External Integrations
None — packrlman is fully self-contained. TensorBoard reads local `./tb/` logs.

## Database Schema
Not applicable.

## Configuration
- Board size, wall density, ghost count, tick rate, FPS, cell size, and reward constants are hardcoded as module-level constants or class defaults (no YAML/TOML config).
- RL hyperparameters live inline in `rl/train_ppo.py`.
- Determinism flows from a single `random.Random(seed)` owned by `PacmanGame` and threaded into `generate_map`.

## Deployment Architecture
Local desktop / workstation. No hosting target.

## Testing Strategy
- `tests/test_game.py` — core rules (movement, collision, dot collection, terminal idempotency).
- `tests/test_map_gen.py` — reachability and ghost spawn invariants.
- `tests/test_gym_env.py` — gymnasium wrapper contract.
- `tests/test_integration.py` — end-to-end episode.
- `pygame_app.py` and the training loop itself are not unit-tested (visual / long-running).

## Key Risks
- The "no pygame in core" invariant is convention-enforced; a careless `import pygame` would break headless tests and RL training. A pre-commit grep could enforce it.
- Reward shaping is constant (not scaled by remaining dots) — susceptible to policy exploits.
- Map generation can fall back to no interior walls; an unlucky seed can still fail (raises `RuntimeError`).

---
*Based on codebase analysis performed 2026-04-18.*
