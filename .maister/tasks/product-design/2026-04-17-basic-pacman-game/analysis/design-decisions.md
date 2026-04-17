# Design Decisions

All five decision areas resolved with the recommended alternatives. One extra decision added on seeded RNG.

## Selected Approach (summary)

A small Python package built around a **pygame-free `PacmanGame` core** with an atomic `step(action)` interface, consumed by a **thin pygame shell** for human play. State is a readable **dict**, with a `to_tensor()` helper for future DQN training. Maps are randomly generated via **random walls + guaranteed border + minimum spawn distance + BFS connectivity check**. Rendering uses **pygame primitives only** (rects + circles + text). An optional `seed` parameter makes maps reproducible.

## Key Decisions

| Area | Decision | Rationale |
|---|---|---|
| Architecture | `PacmanGame` core + thin `pygame_app.py` shell (1B) | Satisfies future RL requirement cheaply; core is unit-testable without a display |
| Tick model | Atomic `step(action)` driven by wall-clock (human) or direct calls (RL) (2C) | One tick semantic; arcade feel preserved; no dual-timing logic |
| State shape | Canonical dict + `to_tensor()` helper (3C) | Readable and debuggable primary; RL-ready without forcing one shape to do both jobs |
| Map generation | Border walls + wall_density + min-spawn-distance + BFS check (4B) | Prevents unwinnable and instant-loss maps; ~10 extra lines over baseline |
| Rendering | Pygame primitives (rects, circles, font) (5A) | Zero asset files; matches the "simple" scope |
| Reproducibility | Optional `seed: int \| None` parameter | Trivial to add; useful for both playtesting and future RL |

## Trade-offs Accepted
- Two modules instead of one (core + shell) in exchange for RL-readiness.
- Player can only move one tile per tick (~150 ms) in exchange for clean step semantics and sane ghost pacing.
- Prototype visuals (no sprite art) in exchange for zero asset management.
- Maps may occasionally need regeneration (BFS failure) in exchange for guaranteed winnability.

## Deferred (explicitly out of scope)
- Full `gymnasium.Env` wrapper (add when training actually begins).
- Smarter ghost AI / pathfinding.
- Sprites, animations, sound.
- Power pellets, multiple levels, high-score persistence.
- Structured maze generation (revisit only if random feels bad).

See `analysis/alternatives.md` for the full alternative-by-alternative analysis.
