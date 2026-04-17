# Personas

## Persona 1: The Human Player (primary)
- **Role**: Casual player — likely the developer/user themselves or a friend.
- **Goals**: Quick entertainment; start a round, clear dots, beat the ghost.
- **Pain points**: Sluggish/unresponsive controls; unwinnable maps; unclear game state (am I winning? why did I die?).
- **Key journey**: Launches `python main.py` → pygame window opens with a freshly generated map → moves player with arrow keys to collect dots while dodging ghosts → sees WIN/LOSE overlay → presses `R` to play again.

## Persona 2: The RL Researcher / Future Self (secondary, latent)
- **Role**: Developer who wants to train a Deep Q-Learning agent against this game later.
- **Goals**: Treat the game as an environment — reset it, step it with an action, read back the state and a reward, detect terminal states, ideally run it headlessly and fast.
- **Pain points**: Game state locked inside render loop; no clean reset; state only accessible via screen pixels; rendering/input tied to logic so can't run headless.
- **Key journey (future, not built now)**: `from pacman import PacmanGame; env = PacmanGame(); state = env.reset(); state, reward, done = env.step(action)` → loop for thousands of episodes.

## Design implications from personas
- The human player dominates Phase 7 UI decisions.
- The RL researcher dominates architecture decisions in Phase 6 — specifically, a `PacmanGame` core class with `reset()`, `step(action)`, and `get_state()` that does NOT depend on pygame. The pygame loop becomes a thin shell around this core.
