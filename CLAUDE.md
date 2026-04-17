# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install: `pip install -r requirements.txt`

Run the game: `python main.py`

Run tests: `pytest` (or `pytest tests/test_game.py::test_name` for a single test).

## Architecture

Pacman implementation with a strict **headless core / presentation shell** split. The layering is load-bearing — preserve it.

- `game/types.py` — `Action`, `Status` enums. Pure data.
- `game/map_gen.py` — Procedural map generator. Returns `(walls, dots, player_pos, ghost_positions)`. Uses BFS to verify every dot is reachable from the player spawn; retries with decreasing wall density, falling back to no interior walls as last resort. Ghosts are placed with a Manhattan-distance threshold from the player that degrades from `MIN_SPAWN_DIST=5` down to 2 if needed.
- `game/core.py` — `PacmanGame`: deterministic rules engine with atomic `step(action) -> (state, reward, done)` semantics. Order within a tick: player move → dot collect → ghost moves → collision check → win check → time penalty. Terminal steps are idempotent. `to_tensor()` returns a `(4, H, W)` float32 array with channels `walls, dots, player, ghosts` (ghost overlap is summed, not clipped).
- `game/pygame_app.py` — The **only** module permitted to import pygame. Imports happen lazily inside `run()` so the core is importable without pygame installed. Rendering at `FPS=60`, game logic advances every `TICK_MS=150` ms; between ticks the most recent arrow-key input is buffered as `pending_action`.

**Invariant:** `game/types.py`, `game/map_gen.py`, and `game/core.py` MUST NOT import pygame. Tests rely on this to exercise game logic headlessly. Determinism flows from a single `random.Random(seed)` owned by `PacmanGame` and threaded into `generate_map`.

Reward constants (`TIME_PENALTY`, `DOT_REWARD`, `WIN_BONUS`, `LOSS_PENALTY`) live in `core.py` and shape the RL signal — the `to_tensor` + reward API suggests this game is intended as an RL environment.
