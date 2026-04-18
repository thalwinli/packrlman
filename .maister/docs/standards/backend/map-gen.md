# Map Generation Rules

### BFS-verified reachability
`generate_map` must produce a map where every dot is reachable from the player spawn. Reachability is verified with BFS; if a candidate map fails, wall density is decreased and generation retried. The last-resort fallback is zero interior walls. If that also fails, raise `RuntimeError` — do not return an unreachable map.

### Ghost spawn via BFS path distance
Ghosts are placed at cells whose BFS path distance from the player >= `MIN_SPAWN_DIST` (default 5). On failure the threshold degrades down to `MIN_SPAWN_DIST_FLOOR` (2). Use BFS path distance, not Manhattan distance — corridors matter.

*Source: CLAUDE.md + game/map_gen.py. (Note: a prior CLAUDE.md revision described Manhattan distance; BFS path distance is the current implementation per recent commits.)*
