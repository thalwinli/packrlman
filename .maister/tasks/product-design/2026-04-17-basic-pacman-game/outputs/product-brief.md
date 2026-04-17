# Product Brief: Basic Pacman Game (Python + pygame)

## Layer 0: Core Brief

### Problem Statement
Build a simple Pacman-style arcade game in Python using pygame. A single player navigates a randomly generated grid-based map, collecting dots while avoiding randomly-moving ghosts. Clearing all dots wins; touching a ghost loses. The game must also serve as a future **reinforcement learning environment** — state must be programmatically accessible so a Deep Q-Learning agent can later be trained against it. Training itself is out of scope; architectural readiness is in scope.

### Target Users
- **Human Player (primary)**: Casual player launching `python main.py` for a quick round of arcade play.
- **RL Researcher / Future Self (secondary, latent)**: Developer who will later train a DQN agent against this game by stepping it programmatically. See Layer 1.

### Feature Overview
A small Python package (`pacman/`) with a pygame-free `PacmanGame` core and a thin `pygame_app.py` shell:
- 20x15 tile grid, randomly generated each round (border walls + ~25% wall density + BFS connectivity check + minimum player-ghost spawn distance).
- Arrow-key input, one move per ~150 ms tick; ghosts move each tick to a uniformly-random valid non-wall neighbor.
- Collision with a ghost → "GAME OVER" overlay; all dots collected → "YOU WIN" overlay. Press `R` to regenerate a new map.
- `PacmanGame` exposes `reset()`, `step(action) → (state, reward, done)`, `get_state()` (dict), and `to_tensor()` (numpy `(4, H, W)`).
- Optional `seed` parameter for reproducible maps.
- Rendering via pygame primitives only (rects, circles, font) — no asset files.

### Constraints
- Language/framework: Python 3 + pygame>=2.5 + numpy>=1.24.
- Scope: intentionally minimal (no audio, menus, levels, power pellets, sprite art, or ghost pathfinding).
- Input: arrow keys + `R` + `ESC` only.
- Architecture: game core MUST NOT import pygame. Only `pygame_app.py` may import pygame.
- All randomly generated maps MUST be winnable (BFS-verified).

### Success Criteria
1. `python main.py` launches a pygame window with a fresh random map.
2. Arrow keys move the player one tile per tick; walls block movement.
3. All generated maps are winnable (dots reachable from player spawn).
4. Ghosts spawn at Manhattan distance ≥ 5 from the player when feasible.
5. Collecting a dot increments the HUD score.
6. Win/lose overlays appear on end state; `R` regenerates a new map.
7. Game renders at stable ~60 FPS.
8. `pacman.game` imports and runs with pygame uninstalled.
9. `PacmanGame(seed=42).reset()` is deterministic.
10. `game.step(action)` callable headlessly; returns `(state, reward, done)`.

### Acceptance Criteria
See `analysis/feature-spec.md` Section 4 for the full list (13 criteria). The above success criteria are the user-observable subset.

---

## Layer 1: Persona Cards

### Human Player (primary)
- **Goals**: Quick entertainment — clear dots, beat the ghosts.
- **Pains**: Unresponsive controls, unwinnable maps, unclear end-state feedback.
- **Journey**: `python main.py` → gameplay with arrow keys → WIN or LOSE overlay → `R` to replay.

### RL Researcher / Future Self (secondary, latent)
- **Goals**: Use game as a Gym-like env; `reset()`, `step()`, read state + reward, detect terminal states, run thousands of episodes.
- **Pains**: State trapped in render loop; no clean reset; can't run headless.
- **Journey (future, not built)**: `env = PacmanGame(seed=…); state = env.reset(); state, reward, done = env.step(action)`.

Full detail: `analysis/personas.md`.

---

## Layer 2: Design Decisions

| Area | Decision | Why |
|---|---|---|
| Architecture | `PacmanGame` core + thin pygame shell (1B) | RL-ready at minimal cost; core unit-testable headless |
| Tick model | Atomic `step()` with two drivers (2C) | One tick semantic; arcade feel for humans + fast RL loop |
| State shape | Dict canonical + `to_tensor()` helper (3C) | Readable debugging + DQN-ready without forcing one shape |
| Map generation | Border walls + wall_density + min-spawn-distance + BFS (4B) | Prevents unwinnable + instant-loss maps cheaply |
| Rendering | Pygame primitives (5A) | Zero assets; matches "simple" scope |
| Reproducibility | Optional `seed: int \| None` parameter | Trivial; helps playtesting + future RL |

Full alternative analysis: `analysis/alternatives.md`. Decision rationale: `analysis/design-decisions.md`.

---

## Layer 3: Mockup References

ASCII mockups at `analysis/mockups/ascii-mockups.md`:
- Playing state (20x15 grid with walls, dots, player, 3 ghosts, HUD)
- WIN overlay
- LOSE overlay

(Visual companion not used — Node.js not available on this system; ASCII fallback per graceful-degradation policy.)

---

## References

- `analysis/design-context.md` — unified context synthesis
- `analysis/problem-statement.md` — refined problem, constraints, success criteria, assumptions
- `analysis/personas.md` — persona cards + user journeys
- `analysis/alternatives.md` — full brainstormer output (5 decision areas, 2-3 alternatives each)
- `analysis/design-decisions.md` — selected approach + trade-offs + deferred items
- `analysis/feature-spec.md` — 4-section implementation spec (architecture, core logic, pygame shell, acceptance criteria)
- `analysis/mockups/ascii-mockups.md` — ASCII wireframes

---

## Deferred (explicitly out of scope for initial build)
- Full `gymnasium.Env` wrapper (add when training begins).
- Smarter ghost AI / pathfinding.
- Sprite art, animations, sound.
- Power pellets, multiple levels, high-score persistence.
- Structured maze generation (revisit only if random feels bad).
