# Design Alternatives: Basic Pacman Game

Scope reminder: small game, 5 decision areas, pick the simplest reasonable option for each while honoring the RL-readiness constraint. One page max per area.

---

## 1. Code Architecture / Separation

How to structure game logic vs. pygame rendering/input.

### Alt 1A: Monolithic `main.py`
All logic, rendering, and input handling in a single file and loop.
- **Pros**: Fewest files; fastest to write; easiest to read end-to-end.
- **Cons**: Directly violates the RL-readiness constraint — state is trapped inside the render loop; no headless path; will require rewrite later.
- **Evidence**: Persona 2 explicitly lists "state locked inside render loop" as a pain point.

### Alt 1B: `PacmanGame` core + thin pygame shell (RECOMMENDED)
Pure-Python `PacmanGame` class owns state and rules (`reset()`, `step(action)`, `get_state()`); a separate `pygame_app.py` polls input, calls `step`, and renders `get_state()`. No pygame imports in the core.
- **Pros**: Satisfies RL constraint with minimal ceremony; core is unit-testable without a display; future Gym wrapper is ~30 lines on top.
- **Cons**: Two modules instead of one; small amount of glue code.
- **Evidence**: Problem statement success criterion #8 and persona 2 journey effectively describe this shape.

### Alt 1C: Full Gym-compatible `gym.Env` interface now
Implement `gymnasium.Env` fully (action_space, observation_space, render modes, seeding).
- **Pros**: Drop-in for any RL library today.
- **Cons**: Pulls in `gymnasium` dependency and conventions (Box/Discrete spaces, render modes, info dicts) for a game that may never be trained; over-engineered for stated scope.

**Recommendation: 1B.** Get 90% of the RL benefit for 10% of the complexity. Keep the core pygame-free; write a Gym wrapper later if training actually happens.

---

## 2. Game Loop / Tick Model

How time advances for player vs. ghosts vs. render.

### Alt 2A: Fixed 60 FPS render, ghosts tick every N frames
Render every frame; ghosts move every ~15–20 frames (~3–4 moves/sec); player moves one tile per arrow-key press (with key-repeat gated by a small cooldown or tick boundary).
- **Pros**: Feels like a real-time game; stable framerate; matches success criterion #7; ghost speed is a single tunable constant.
- **Cons**: Need to define what "one tick" means for `step()` in RL mode — typically "one ghost tick" — slight asymmetry between human real-time play and RL stepping.

### Alt 2B: Pure turn-based (player moves, then ghosts move)
Every player input advances one tick for everyone. No timer.
- **Pros**: Cleanest RL semantics — `step(action)` = exactly one tick; trivial to reason about; no frame-timing code.
- **Cons**: Feels like a puzzle, not Pacman; ghosts don't press you under time pressure; mild UX regression vs. user expectation of "arcade game."

### Alt 2C: Event-driven, decoupled human vs. agent modes (RECOMMENDED)
Core exposes `step(action)` as one atomic tick (player move + ghost moves + collision resolution). Pygame shell runs at 60 FPS, reads buffered arrow input, and calls `step()` on a fixed tick timer (e.g., every 150 ms). RL code calls `step()` directly as fast as it wants.
- **Pros**: Keeps arcade feel for humans AND gives RL the clean one-call-per-tick model; ghost speed = the tick interval, trivially configurable; no dual-timing logic in the core.
- **Cons**: Player can only move once per tick (feels slightly laggy at long tick intervals — mitigate with ~100–150 ms default).

**Recommendation: 2C.** One semantic tick, two drivers (wall clock for humans, loop-as-fast-as-possible for RL).

---

## 3. State Representation (`get_state()` return shape)

### Alt 3A: Dict of entities
```python
{"player": (x,y), "ghosts": [(x,y), ...], "dots": {(x,y), ...},
 "walls": {(x,y), ...}, "score": int, "status": "playing"|"won"|"lost"}
```
- **Pros**: Human-readable; trivial to render; tiny; easy to serialize/debug.
- **Cons**: RL code will still want a tensor — every training step must convert.

### Alt 3B: Numpy grid tensor only
Single `(H, W)` or `(C, H, W)` int/float array with channel or value encoding per cell type.
- **Pros**: Direct DQN input; no conversion at train time.
- **Cons**: Loses semantic clarity; score/status must ride alongside anyway; harder to render/debug.

### Alt 3C: Both — dict is canonical, plus a `to_tensor()` helper (RECOMMENDED)
`get_state()` returns the dict. A separate `PacmanGame.to_tensor(state)` (or `get_observation()`) produces a `(C, H, W)` numpy array with channels for walls / dots / player / ghosts.
- **Pros**: Best of both — readable canonical state for rendering/tests, tensor on demand for RL; conversion logic lives in one place and is testable.
- **Cons**: Two accessors instead of one (negligible).

**Recommendation: 3C.** Dict is primary. Tensor is a pure function of the dict, added as a helper method. Keeps the core simple while removing the main friction point for future DQN work.

---

## 4. Map Generation Details

Base algorithm is fixed: random walls + BFS connectivity check, regenerate on failure. Remaining knobs:

### Alt 4A: Minimal — wall density only
Single `wall_density` float (e.g., 0.25). No forced border. Place player and ghosts on random empty connected cells.
- **Pros**: Simplest; one knob.
- **Cons**: Map can "leak" at edges visually; player can spawn adjacent to a ghost (instant-loss maps possible).

### Alt 4B: Guaranteed border walls + density + min-spawn-distance (RECOMMENDED)
Border always wall. Interior cells wall with probability `wall_density` (~0.25). Player spawns on a random empty cell; ghosts spawn on empty cells at Manhattan distance ≥ K (e.g., 5) from player. Remaining empty cells get dots. BFS check after generation; regenerate up to M times, then lower density and retry.
- **Pros**: Fixes both issues in 4A with ~10 extra lines; makes games actually winnable in practice; deterministic framing for the player.
- **Cons**: A couple more parameters.

### Alt 4C: Structured maze (e.g., recursive backtracker, symmetric layout)
Generate proper corridors like real Pacman.
- **Pros**: Prettier, more "Pacman-feel."
- **Cons**: Meaningfully more code; out of scope per "keep it simple"; not needed for RL.

**Recommendation: 4B.** Tiny addition over the baseline, prevents the two obvious failure modes (ghost-on-spawn, no-border). Defer 4C unless the game feels bad.

---

## 5. Rendering Approach

### Alt 5A: Primitive rectangles + circles (RECOMMENDED)
Walls = filled rects, dots = small circles, player = yellow circle, ghosts = colored circles/rects. Score and WIN/LOSE via `pygame.font`.
- **Pros**: Zero asset files; all drawing in ~20 lines; trivial to tweak; no licensing issues; perfectly readable at 20x15.
- **Cons**: Looks like a prototype (acceptable per scope).

### Alt 5B: Sprite images (PNG assets)
Load sprites for player/ghosts/walls/dots.
- **Pros**: Looks nicer; room for animation later.
- **Cons**: Requires sourcing/creating assets; asset directory; load paths; more failure modes (missing files). Overkill for stated scope.

### Alt 5C: Tile-based character rendering (ASCII-style via font)
Render each cell as a character glyph (`#`, `.`, `P`, `G`).
- **Pros**: Even simpler than 5A in some ways; trivially "dumps the grid."
- **Cons**: Less arcade-feel for Persona 1; font metrics add minor alignment work.

**Recommendation: 5A.** Matches "simple, UI-focused" best. Pure pygame primitives, no external assets, good enough for human play and irrelevant to RL (which reads state, not pixels).

---

## Summary of Recommendations

| Area | Pick | One-line rationale |
|---|---|---|
| Architecture | 1B: core + pygame shell | Satisfies RL constraint cheaply |
| Tick model | 2C: atomic `step()`, two drivers | One tick semantics, arcade feel + fast RL |
| State shape | 3C: dict + `to_tensor()` helper | Readable primary, tensor on demand |
| Map gen | 4B: border + density + min-spawn-dist | Prevents obvious bad maps |
| Rendering | 5A: primitives | Simplest; no assets |

## Key Assumptions Behind Recommendations
- RL training may or may not happen; we pay only the minimum tax to keep the door open.
- ~20x15 grid is small enough that both dict and tensor state are trivially cheap.
- Human play at ~150 ms per tick feels responsive enough; revisit if playtesting disagrees.

## Deferred Ideas (Out of Scope)
- Full `gymnasium.Env` wrapper (add when actual training starts).
- Smarter ghost AI / pathfinding (explicitly carved out).
- Sprite art, animations, sound (explicitly carved out).
- Power pellets, levels, scoring tiers (explicitly carved out).
- Structured maze generation (4C) — revisit only if random maps feel bad.
- Seeded RNG for reproducibility — trivial to add later, worth mentioning to spec.
