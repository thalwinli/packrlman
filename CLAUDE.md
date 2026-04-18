# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Coding Standards & Conventions

Read @.maister/docs/INDEX.md before starting any task. It indexes the project's coding standards and conventions:
- Coding standards organized by domain (frontend, backend, testing, etc.)
- Project vision, tech stack, and architecture decisions

Follow standards in `.maister/docs/standards/` when writing code — they represent team decisions. If standards conflict with the task, ask the user.

### Standards Evolution

When you notice recurring patterns, fixes, or conventions during implementation that aren't yet captured in standards — suggest adding them. Examples:
- A bug fix reveals a pattern that should be standardized (e.g., "always validate X before Y")
- PR review feedback identifies a convention the team wants enforced
- The same type of fix is needed across multiple files
- A new library/pattern is adopted that should be documented

When this happens, briefly suggest the standard to the user. If approved, invoke `/maister:standards-update` with the identified pattern.

## Maister Workflows

This project uses the maister plugin for structured development workflows. When any `/maister:*` command is invoked, execute it via the Skill tool immediately — do not skip workflows for "straightforward" tasks. The user chose the workflow intentionally; complexity assessment is the workflow's job.

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
