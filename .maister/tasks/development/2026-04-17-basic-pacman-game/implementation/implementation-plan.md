# Implementation Plan: Basic Pacman Game (Python + pygame)

## Overview

- **Total Task Groups:** 5
- **Estimated Total Steps:** ~35
- **Expected Tests:** ~12-18 (unit + smoke/integration)
- **Scope:** Greenfield. Small, self-contained package. Low risk, simple complexity.
- **Architecture (already decided):** `pacman/` package with pygame-free core (`game.py`, `map_gen.py`, `types.py`) + thin pygame shell (`pygame_app.py`), driven by top-level `main.py`.

### Source of Truth

- Spec: `C:/Code/test/.maister/tasks/product-design/2026-04-17-basic-pacman-game/analysis/feature-spec.md`
- Decisions: `C:/Code/test/.maister/tasks/product-design/2026-04-17-basic-pacman-game/analysis/design-decisions.md`
- Brief: `C:/Code/test/.maister/tasks/product-design/2026-04-17-basic-pacman-game/outputs/product-brief.md`
- Mockups: `C:/Code/test/.maister/tasks/product-design/2026-04-17-basic-pacman-game/analysis/mockups/ascii-mockups.md`

### Acceptance Criteria Mapping (from feature-spec.md Section 4)

| AC # | Description | Covered by Group |
|------|-------------|------------------|
| 1 | `python main.py` launches pygame window | 1, 4 |
| 2 | Arrow keys move player per tick; walls block | 3, 4 |
| 3 | All maps winnable (BFS-verified) | 2 |
| 4 | Ghost spawn Manhattan distance >= 5 when feasible | 2 |
| 5 | Ghosts move to random valid neighbor per tick | 3 |
| 6 | Dot collection removes dot, increments score, shown in HUD | 3, 4 |
| 7 | WIN overlay + `R` regenerates | 3, 4 |
| 8 | LOSE overlay + `R` regenerates | 3, 4 |
| 9 | Stable ~60 FPS render | 4 |
| 10 | Core has zero pygame imports; importable without pygame | 1, 5 |
| 11 | `get_state()` dict + `to_tensor()` `(4,H,W)` ndarray | 3 |
| 12 | Seeded map is reproducible | 2, 5 |
| 13 | `step()` callable standalone returns `(state, reward, done)` | 3, 5 |

---

## Implementation Steps

### Task Group 1: Project Scaffolding
**Dependencies:** None
**Estimated Steps:** 6
**Tests:** 0 (pure scaffolding; correctness verified in later groups)

- [x] 1.0 Establish project structure and package skeleton
  - [x] 1.1 Create `requirements.txt` at repo root with:
    - `pygame>=2.5`
    - `numpy>=1.24`
  - [x] 1.2 Create `pacman/__init__.py` (empty or with `__all__ = []`)
  - [x] 1.3 Create empty module stubs with module-level docstrings and no pygame imports in core:
    - `pacman/types.py`
    - `pacman/map_gen.py`
    - `pacman/game.py`
    - `pacman/pygame_app.py` (the ONLY file that may `import pygame`)
  - [x] 1.4 Create `main.py` entry point (5-line launcher):
    ```python
    from pacman.pygame_app import run

    if __name__ == "__main__":
        run()
    ```
  - [x] 1.5 Create `tests/__init__.py` and `tests/` directory for pytest discovery
  - [x] 1.6 Verify structure: `python -c "import pacman"` succeeds (import does NOT fail; pygame shell not yet imported)

**Acceptance Criteria:**
- Directory tree matches feature-spec.md Section 1 layout exactly
- `python -c "import pacman.types, pacman.map_gen, pacman.game"` succeeds with pygame NOT installed (core modules must stay pygame-free from day one — even as stubs)
- `requirements.txt` installable

---

### Task Group 2: Types & Map Generation (`types.py`, `map_gen.py`)
**Dependencies:** Group 1
**Estimated Steps:** 7
**Tests:** 5

- [x] 2.0 Implement types and random map generator with BFS connectivity
  - [x] 2.1 Write 5 focused tests in `tests/test_map_gen.py`:
    - `test_border_walls_always_present` — every border cell is a wall for varied sizes
    - `test_all_dots_reachable_from_player` — BFS from player reaches every dot cell
    - `test_ghost_min_spawn_distance` — ghost Manhattan distance from player >= 5 on default params (tolerate fallback to >=2 on dense maps)
    - `test_ghost_count_matches_request` — exactly `num_ghosts` ghosts returned
    - `test_seeded_generation_is_deterministic` — same seed + same params → identical `(walls, dots, player, ghosts)` tuple
  - [x] 2.2 Implement `pacman/types.py`:
    - `Action` enum: `UP=0, DOWN=1, LEFT=2, RIGHT=3, NOOP=4`
    - `Status` enum: `PLAYING="playing", WON="won", LOST="lost"`
  - [x] 2.3 Implement `pacman/map_gen.py` constants:
    - `MIN_SPAWN_DIST = 5`
    - `MAX_REGEN_ATTEMPTS = 20`
  - [x] 2.4 Implement `generate_map(width, height, wall_density, num_ghosts, rng) -> (walls, dots, player_pos, ghost_positions)`:
    - Draw full border walls (all `(x, 0)`, `(x, height-1)`, `(0, y)`, `(width-1, y)` cells)
    - For each interior cell: wall with probability `wall_density` (default `0.25`)
    - Collect empty cells, pick player spawn uniformly at random
    - Pick ghosts uniformly from empties with Manhattan distance `>= MIN_SPAWN_DIST`; if fewer candidates than `num_ghosts`, decrement distance threshold by 1 down to 2
    - Remaining empties become dots
  - [x] 2.5 Implement BFS connectivity check:
    - BFS from `player_pos` over non-wall neighbors (4-connected)
    - If any dot is unreachable, regenerate (up to `MAX_REGEN_ATTEMPTS`)
    - If still failing, reduce `wall_density` by `0.05` and retry
  - [x] 2.6 Helper: `_manhattan(a, b)` in `map_gen.py` for tests and ghost placement
  - [x] 2.7 Ensure all 5 tests pass: `pytest tests/test_map_gen.py -v`
    - Run ONLY the 5 tests written in 2.1 (NOT entire suite)

**Acceptance Criteria:**
- All 5 tests pass
- `pacman/types.py` and `pacman/map_gen.py` contain zero pygame imports
- `generate_map(..., rng=random.Random(42))` returns identical output across repeated calls
- Reference feature-spec.md Section 2 "Map generation"

---

### Task Group 3: Core Game Logic (`game.py`)
**Dependencies:** Group 2
**Estimated Steps:** 9
**Tests:** 7

- [x] 3.0 Implement `PacmanGame` class with atomic step semantics
  - [x] 3.1 Write 7 focused tests in `tests/test_game.py`:
    - `test_reset_returns_state_dict_with_expected_keys` — keys: `width, height, walls, dots, player, ghosts, score, status, tick`
    - `test_step_returns_tuple_state_reward_done` — `(dict, float, bool)` shape
    - `test_wall_blocks_player_movement` — craft/seed a game where a wall is adjacent; `step()` toward wall leaves player stationary
    - `test_dot_collection_increments_score_and_removes_dot` — step onto a dot → score +1, dot gone, reward +1.0
    - `test_ghost_collision_sets_lost_and_negative_reward` — force ghost onto player's cell → `status == "lost"`, reward <= -10.0, `done == True`
    - `test_all_dots_collected_sets_won` — step onto last dot → `status == "won"`, `done == True`, reward includes +10.0
    - `test_to_tensor_shape_is_4_H_W` — `to_tensor()` returns numpy array with shape `(4, height, width)` (channels: walls, dots, player, ghosts)
  - [x] 3.2 Implement `PacmanGame.__init__(width=20, height=15, wall_density=0.25, num_ghosts=3, seed=None)`:
    - Store config; initialize `self._rng = random.Random(seed)` (None → system entropy)
    - Call `self.reset()` so instance is immediately usable
  - [x] 3.3 Implement `reset()`:
    - Call `generate_map(...)` with `self._rng`
    - Reset `score=0, tick=0, status=Status.PLAYING`
    - Return `self.get_state()`
  - [x] 3.4 Implement `step(action: Action) -> tuple[dict, float, bool]` per feature-spec.md Section 2 "Tick semantics":
    1. Compute target cell from action (NOOP → stay); if wall or out of bounds → stay
    2. If target cell has a dot: remove it, `score += 1`, `reward += 1.0`
    3. For each ghost: pick uniformly at random from non-wall neighbor cells (or stay if none); ghosts may overlap each other
    4. Collision: if any ghost shares player's cell → `status = LOST`, `reward -= 10.0`, `done = True`
    5. If no dots remain → `status = WON`, `reward += 10.0`, `done = True`
    6. Otherwise `reward -= 0.01` per tick
    - Increment `self.tick`
    - Return `(self.get_state(), reward, done)`
  - [x] 3.5 Implement `get_state() -> dict` returning dict per feature-spec.md Section 2 "State dict shape" (use string values for status, e.g. `self.status.value`)
  - [x] 3.6 Implement `to_tensor() -> np.ndarray` shape `(4, H, W)`, dtype `float32` or `uint8`:
    - Channel 0: walls (1 where wall)
    - Channel 1: dots (1 where dot)
    - Channel 2: player (1 at player cell)
    - Channel 3: ghosts (1 at any ghost cell; sums if multiple — or just clipped to 1, document choice)
  - [x] 3.7 Verify zero pygame imports in `game.py` (grep / visual check)
  - [x] 3.8 Run tests: `pytest tests/test_game.py -v` — ONLY these 7 tests
  - [x] 3.9 Ensure all 7 tests pass

**Acceptance Criteria:**
- All 7 tests pass
- `pacman/game.py` has zero pygame imports
- `PacmanGame().step(Action.UP)` works standalone with no display
- Covers acceptance criteria 2, 5, 6, 11, 13

---

### Task Group 4: Pygame Shell (`pygame_app.py`)
**Dependencies:** Group 3
**Estimated Steps:** 8
**Tests:** 0 automated (pygame rendering is manually verified — documented smoke check below)

- [x] 4.0 Implement pygame shell: input, tick timer, rendering, overlays
  - [x] 4.1 Add constants at top of `pygame_app.py`:
    - `CELL_PX = 28`, `TICK_MS = 150`, `FPS = 60`, `HUD_PX = 32`
    - Color constants: `BG=(0,0,0)`, `WALL=(30,30,200)`, `DOT=(255,255,255)`, `PLAYER=(255,230,0)`, `GHOST=(220,50,50)`, `WIN_TEXT=(50,220,50)`, `LOSE_TEXT=(220,50,50)`
  - [x] 4.2 Implement `run()` startup:
    - `pygame.init()`
    - Create window: `(width * CELL_PX, height * CELL_PX + HUD_PX)`
    - Instantiate `game = PacmanGame()` with defaults; `game.reset()`
    - Create `pygame.time.Clock()` and `font = pygame.font.SysFont(None, 24)`
    - Track `pending_action = None`, `last_tick = pygame.time.get_ticks()`
  - [x] 4.3 Implement event polling per frame:
    - `QUIT` → break
    - `KEYDOWN K_ESCAPE` → break
    - `KEYDOWN K_UP/DOWN/LEFT/RIGHT` → overwrite `pending_action` (newest wins)
    - `KEYDOWN K_r` → if `status != PLAYING`, `game.reset()` and clear `pending_action`
  - [x] 4.4 Implement tick timer (once per frame):
    - If `now - last_tick >= TICK_MS` AND `state["status"] == "playing"`:
      - `action = pending_action or Action.NOOP`
      - `game.step(action)`; `pending_action = None`; `last_tick = now`
  - [x] 4.5 Implement rendering (reference mockup: `analysis/mockups/ascii-mockups.md` section 1):
    - Fill background black
    - Draw walls as blue rects at `(x*CELL_PX, y*CELL_PX, CELL_PX, CELL_PX)`
    - Draw dots as white circles radius 3 at cell center
    - Draw player as yellow circle radius `CELL_PX//2 - 2` at cell center
    - Draw each ghost as red circle radius `CELL_PX//2 - 3` at cell center
    - Render HUD bar at `y = height * CELL_PX`, draw text `f"Score: {score}   Status: {status}"`
  - [x] 4.6 Implement game-end overlays (reference mockups sections 2 & 3):
    - On `WON`: semi-transparent dark rect covering playfield + centered green text `"YOU WIN -- press R"`
    - On `LOST`: same with red text `"GAME OVER -- press R"`
    - Use `pygame.Surface(..., pygame.SRCALPHA)` for transparency
  - [x] 4.7 Frame cap: `clock.tick(60)` at end of main loop; call `pygame.quit()` on exit
  - [x] 4.8 Manual smoke check (document in work log, not automated):
    - `python main.py` opens window
    - Arrow keys move player; walls block
    - Dots disappear and score increments
    - Collect all dots → WIN overlay
    - Step into ghost → LOSE overlay
    - `R` regenerates map after win/lose
    - `ESC` and window close both exit cleanly

**Acceptance Criteria:**
- `python main.py` launches, plays, ends cleanly
- Covers acceptance criteria 1, 2, 6, 7, 8, 9
- `pygame_app.py` is the ONLY module importing pygame

---

### Task Group 5: Smoke / Integration Tests & Isolation Verification
**Dependencies:** Groups 1-4

- [x] 5.0 Final cross-cutting tests and pygame-isolation verification
  - [x] 5.1 Review existing tests (5 from Group 2 + 7 from Group 3 = 12 total). Identify gaps for THIS feature only — do NOT write exhaustive coverage
  - [x] 5.2 Write up to 5 additional strategic tests in `tests/test_integration.py`:
    - `test_core_imports_without_pygame` — use `unittest.mock` to make `import pygame` raise `ImportError`, then verify `import pacman.game`, `import pacman.map_gen`, `import pacman.types` still succeed (AC 10)
    - `test_seeded_game_produces_identical_map` — `PacmanGame(seed=42).reset()` twice returns structurally identical `walls`, `dots`, `player`, `ghosts` (AC 12)
    - `test_seeded_game_step_sequence_deterministic` — with fixed seed, running the same sequence of actions produces identical `(state, reward, done)` tuple stream
    - `test_full_episode_runs_to_terminal` — drive the game with a scripted action loop (e.g., random actions with fixed seed) for up to 5000 steps; assert `done` becomes `True` eventually OR episode terminates cleanly
    - `test_step_return_types_strict` — confirm `state` is `dict`, `reward` is `float`, `done` is `bool`
  - [x] 5.3 Run full feature test suite: `pytest tests/ -v` — expect 15-17 tests total, all passing
  - [x] 5.4 Final isolation grep: confirm `import pygame` appears in `pygame_app.py` only (not in `game.py`, `map_gen.py`, `types.py`, `__init__.py`)

**Acceptance Criteria:**
- All feature tests pass (~15-17 total)
- No more than 5 additional tests added in this group
- Covers acceptance criteria 10, 12, 13
- `pygame_app.py` is the sole pygame importer

---

## Execution Order

1. **Group 1: Project Scaffolding** (6 steps, no dependencies)
2. **Group 2: Types & Map Generation** (7 steps, depends on 1)
3. **Group 3: Core Game Logic** (9 steps, depends on 2)
4. **Group 4: Pygame Shell** (8 steps, depends on 3)
5. **Group 5: Smoke / Integration Tests** (4 steps, depends on 1-4)

---

## Standards Compliance

Follow standards from `.maister/docs/standards/` if present:
- `global/` — always applicable
- `python/` — if present, applies to all `.py` files

Project-specific conventions (from spec and decisions):
- Core modules (`game.py`, `map_gen.py`, `types.py`) MUST NOT import pygame under any circumstance.
- `pygame_app.py` is the ONLY allowed pygame importer.
- Prefer stdlib `random.Random` for seeded RNG; do not use `numpy` RNG for map generation (keep numpy dependency scoped to `to_tensor()`).
- Keep public API of `PacmanGame` exactly as specified: `__init__`, `reset`, `step`, `get_state`, `to_tensor`.

---

## Notes

- **Test-Driven where reasonable**: Groups 2 and 3 write tests first (red), then implement (green). Group 4 (rendering) is manually verified — automating pygame window tests is disproportionate to the "simple" scope.
- **Run tests incrementally**: Only run the new tests after each group, not the entire suite (except Group 5 which is explicitly the full-suite gate).
- **Reuse first**: No prior code to reuse (greenfield); however, reuse `generate_map()` from Group 2 inside `PacmanGame.reset()` in Group 3 — do NOT duplicate map-generation logic inside the core class.
- **Mark progress**: Tick off checkboxes as steps complete. Leave the file as the source of truth for resumption.
- **Deferred (do NOT build)**: `gymnasium.Env` wrapper, ghost pathfinding, sprite art, sound, power pellets, multiple levels, high-score persistence.
