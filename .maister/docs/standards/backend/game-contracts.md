# Game Engine Contracts

These are the load-bearing semantic contracts of `PacmanGame`. Changes here ripple into tests and RL training — modify with care.

### Atomic `step(action)` semantics and tick order
`PacmanGame.step(action) -> (state_dict, reward, done)` is atomic. Each tick executes in this fixed order: **player move → dot collect → ghost moves → collision check → win check → time penalty**. Terminal steps are idempotent — calling `step` after `done=True` must not mutate state further or emit additional reward.

### `to_tensor()` channel layout
`to_tensor()` returns a `(4, H, W)` float32 NumPy array with channels **walls, dots, player, ghosts** in that order. Ghost overlap is summed (not clipped), so the ghosts channel can exceed 1.0 when multiple ghosts share a cell. RL models depend on this exact layout.

### Reward constants live in `core.py`
`TIME_PENALTY`, `DOT_REWARD`, `WIN_BONUS`, `LOSS_PENALTY` are defined as module-level constants in `game/core.py` and shape the RL signal. Changing them invalidates existing trained models.

*Source: CLAUDE.md (documented invariants).*
