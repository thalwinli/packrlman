# Feature Specification: Basic Pacman Game

## 1. Architecture & Modules

Project layout:
```
pacman/
  __init__.py
  game.py          # PacmanGame core (NO pygame imports)
  map_gen.py       # random map generation + BFS connectivity check
  types.py         # Action enum, Status enum, simple dataclasses/types
  pygame_app.py    # pygame shell: input polling, rendering, 150 ms tick timer
main.py            # entry point: `python main.py` -> runs pygame shell
requirements.txt   # pygame, numpy
```

Rules:
- `pacman/game.py`, `map_gen.py`, `types.py` MUST NOT import pygame.
- `pacman/pygame_app.py` is the ONLY file that imports pygame. It imports `PacmanGame`, drives it on a wall-clock tick, and renders `get_state()`.
- `main.py` is a 5-line launcher: `from pacman.pygame_app import run; run()`.
- Public API surface of `PacmanGame`: `__init__(width, height, wall_density, num_ghosts, seed=None)`, `reset()`, `step(action)`, `get_state()`, `to_tensor()`.

Dependencies: `pygame>=2.5`, `numpy>=1.24`.

## 2. Core Game Logic (`pacman/game.py` + `map_gen.py` + `types.py`)

**Types (`types.py`):**
```python
from enum import Enum
class Action(Enum): UP=0; DOWN=1; LEFT=2; RIGHT=3; NOOP=4
class Status(Enum): PLAYING="playing"; WON="won"; LOST="lost"
```

**Map generation (`map_gen.py`):**
- `generate_map(width, height, wall_density, num_ghosts, rng) -> (walls, dots, player_pos, ghost_positions)`
- Always draw full border as walls.
- For each interior cell, wall with probability `wall_density` (default 0.25).
- Empty cells = candidates. Pick player spawn uniformly at random from empties.
- Ghost spawns: uniformly random from empties with Manhattan distance `>= MIN_SPAWN_DIST` (default 5) from player; sample without replacement. If fewer than `num_ghosts` candidates, lower distance by 1 and retry (down to 2).
- Remaining empty cells (not player, not ghost) become dots.
- BFS from player over non-wall cells: verify every dot cell is reachable. If not, regenerate (up to 20 attempts). If still failing, lower `wall_density` by 0.05 and retry.

**Core class (`game.py`):**
```python
class PacmanGame:
    def __init__(self, width=20, height=15, wall_density=0.25,
                 num_ghosts=3, seed=None): ...
    def reset(self) -> dict                           # returns get_state()
    def step(self, action: Action) -> tuple[dict, float, bool]  # (state, reward, done)
    def get_state(self) -> dict
    def to_tensor(self) -> np.ndarray                 # shape (4, H, W): walls, dots, player, ghosts
```

**Tick semantics (one `step()` call):**
1. Player attempts move in direction of `action`. If target cell is a wall or out of bounds, player stays. NOOP = stay.
2. If player lands on a dot: remove dot, `score += 1`, `reward += 1.0`.
3. For each ghost: pick uniformly at random from non-wall neighbor cells (or stay if no valid neighbor; ghosts may overlap each other). Move ghost.
4. Collision check: if any ghost now shares the player's cell, `status = LOST`, `reward -= 10.0`, `done = True`.
5. If no dots remain, `status = WON`, `reward += 10.0`, `done = True`.
6. Otherwise `reward -= 0.01` per tick (time penalty, useful for RL; harmless for humans).

**State dict shape (`get_state()`):**
```python
{
  "width": int, "height": int,
  "walls": set[tuple[int,int]],
  "dots": set[tuple[int,int]],
  "player": tuple[int,int],
  "ghosts": list[tuple[int,int]],
  "score": int,
  "status": "playing" | "won" | "lost",
  "tick": int,
}
```

`reset()` generates a fresh random map using the configured (or freshly random) RNG state, resets tick=0, score=0, status=PLAYING, and returns the new state.

## 3. Pygame Shell (`pygame_app.py`)

**Constants:** `CELL_PX = 28`, `TICK_MS = 150`, `FPS = 60`, `HUD_PX = 32`.

**Startup (`run()`):**
1. `pygame.init()`; create window sized `(width * CELL_PX, height * CELL_PX + HUD_PX)`.
2. Instantiate `game = PacmanGame()` with defaults; call `game.reset()`.
3. Main loop at 60 FPS via `pygame.time.Clock`.

**Main loop per frame:**
1. Poll events:
   - `QUIT` → exit loop, `pygame.quit()`.
   - `KEYDOWN` arrow → buffer latest direction in `pending_action` (single slot, newest wins).
   - `KEYDOWN R` → if `status != PLAYING`, call `game.reset()`; clear `pending_action`.
   - `KEYDOWN ESC` → exit.
2. Tick timer: if `now - last_tick >= TICK_MS` AND `status == PLAYING`:
   - `action = pending_action or Action.NOOP`
   - `game.step(action)`; clear `pending_action`; `last_tick = now`.
3. Render (below).
4. `clock.tick(60)`.

**Rendering each frame (read `state = game.get_state()`):**
- Background: black `(0,0,0)`.
- Walls: filled rect blue `(30,30,200)` at `(x*CELL_PX, y*CELL_PX, CELL_PX, CELL_PX)`.
- Dots: white circle radius 3, centered in cell.
- Player: yellow circle `(255,230,0)` radius `CELL_PX//2 - 2`.
- Ghosts: red circle `(220,50,50)` radius `CELL_PX//2 - 3` (same color for all).
- HUD bottom bar: `f"Score: {score}   Status: {status}"` via `pygame.font.SysFont(None, 24)`.
- Overlay on game end:
  - WON → semi-transparent dark rect + centered green text `"YOU WIN — press R"`.
  - LOST → same with red text `"GAME OVER — press R"`.

**Key mapping:** `K_UP/DOWN/LEFT/RIGHT → Action.UP/DOWN/LEFT/RIGHT`. `pending_action` is overwritten on every `KEYDOWN`, so the latest held direction at tick time wins naturally.

## 4. Acceptance Criteria

Given default configuration (`20x15`, 3 ghosts, `wall_density=0.25`):

1. `python main.py` launches a pygame window showing a freshly generated map.
2. Arrow keys move the player one tile per tick (~150 ms). Walls block movement.
3. Every generated map is winnable: all dots reachable from player spawn (BFS-verified during generation).
4. Ghosts spawn at Manhattan distance ≥ 5 from the player when feasible.
5. Ghosts move one tile per tick, picking uniformly among valid non-wall neighbors (stay put if none).
6. Collecting a dot removes it and increments the score; score is shown in the HUD.
7. Collecting all dots: "YOU WIN" overlay; `R` regenerates a new random map.
8. Touching any ghost: "GAME OVER" overlay; `R` regenerates a new random map.
9. Game runs at stable ~60 FPS render.
10. `pacman.game`, `pacman.map_gen`, `pacman.types` have zero pygame imports; `import pacman.game` succeeds with pygame uninstalled.
11. `game.get_state()` returns the documented dict; `game.to_tensor()` returns a `(4, H, W)` numpy array.
12. With a fixed seed, `PacmanGame(seed=42).reset()` produces an identical map across runs.
13. `game.step(Action.X)` is callable standalone (no pygame needed) and returns `(state, reward, done)`.
