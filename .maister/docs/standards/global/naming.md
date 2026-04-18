# Naming Conventions

### File names
All Python modules use lowercase `snake_case`. Test files mirror source module names as `test_<module>.py`.
*Source: 16/16 source files follow this pattern.*

### Classes
PascalCase (e.g., `PacmanGame`, `PacmanEnv`, `SmallCNN`, `Action`, `Status`).

### Functions and methods
snake_case (e.g., `generate_map`, `step`, `to_tensor`, `_is_passable`).

### Constants
Module-level constants use `UPPER_SNAKE_CASE` and are declared at the top of the file, directly after imports (e.g., `TIME_PENALTY`, `DOT_REWARD`, `MIN_SPAWN_DIST`, `TICK_MS`, `FPS`).

### Private members
Private helpers, attributes, and module-level helpers are prefixed with a single underscore (e.g., `_ACTION_DELTA`, `_is_passable`, `_bfs_distances`, `self._walls`, `self._rng`). Tests are permitted to reach into these for scenario setup — this is explicitly sanctioned in the `PacmanGame` docstring.
*Source: Consistent across game/core.py, game/map_gen.py, game/gym_env.py.*
