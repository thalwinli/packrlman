# Problem Statement

## Problem
Build a simple Pacman-style arcade game in Python using pygame. A single player navigates a randomly generated grid-based map, collecting dots while avoiding randomly-moving ghosts. Clearing all dots wins; touching a ghost loses.

The game must also serve as a future **reinforcement learning environment**: state (player position, ghost positions, remaining dots, score, game status) must be programmatically accessible so a Deep Q-Learning agent can later be trained against it. Training is out of scope for this design; architectural readiness is in scope.

## Constraints
- **Language/framework**: Python 3 + pygame.
- **Scope**: Intentionally minimal. No audio, no menus, no multiple levels, no power pellets, no ghost AI beyond random movement.
- **Input**: Arrow keys only (+ one key to restart on game end).
- **Map generation**: Grid-based tiles; random walls with BFS connectivity check; regenerate if dots unreachable.
- **Map size**: TBD in spec (default ~20x15 tiles).
- **Ghost behavior**: Pick any valid (non-wall) neighbor cell at each move tick. No pathfinding, no player tracking.
- **Architectural constraint**: Game logic must be decoupled from rendering/input so the environment can be stepped headlessly by an RL agent later. Aim for a `step(action) -> (state, reward, done)`-style interface, or equivalent accessor.

## Success Criteria
1. Player can move with arrow keys; walls block movement.
2. Random maps are always winnable (all dots reachable from player spawn).
3. Ghosts spawn and move randomly each tick; they never clip through walls.
4. Collecting a dot increments the score and removes the dot visually.
5. Collecting all dots -> WIN overlay; pressing restart key regenerates a new random map.
6. Touching any ghost -> LOSE overlay; pressing restart key regenerates a new random map.
7. Game runs at a stable framerate (~60 FPS render, ghosts tick at a slower configurable rate).
8. Current game state is retrievable via a single accessor (e.g., `game.get_state()`) returning a structured snapshot usable by an RL agent.

## Key Assumptions
- Single-player only; no networked play.
- Desktop only (Windows, macOS, Linux wherever pygame runs).
- No persistence — no save files, no high-score tracking.
- Ghosts do NOT collide with each other (they can overlap).
- Player and ghosts move one tile at a time on a shared grid (discrete movement, not pixel-level continuous).
