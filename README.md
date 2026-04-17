# packrlman

A Pacman. In Python. Because why not.

This is a **funny little vibe-coding project** — the kind of thing that starts with "I wonder if..." at 11pm and ends with a committed repo. No deadlines, no stakeholders, no JIRA. Just dots, ghosts, and a yellow circle that dies a lot.

## What it is

- A perfectly serviceable Pacman clone with procedurally generated mazes.
- A headless game core (`game/core.py`) that knows nothing about pixels.
- A pygame shell (`game/pygame_app.py`) that paints the pixels.
- A `to_tensor()` method sitting there suspiciously, doing nothing yet.

## What it will be (eventually, maybe, probably)

A playground for **reinforcement learning**.

The game is already built for it — deterministic seeded RNG, atomic `step(action) → (state, reward, done)` semantics, a `(4, H, W)` tensor encoding of the world, and reward constants (`DOT_REWARD`, `WIN_BONUS`, `LOSS_PENALTY`, `TIME_PENALTY`) just waiting to shape a policy gradient. One of these days an agent is going to learn to eat dots better than me. That's the dream.

Until then: arrow keys. R to restart. Esc to quit.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Test it

```bash
pytest
```

## Train an agent

The game is now wrapped as a `gymnasium` env (`game/gym_env.py`) with a PPO
training script. Install the extra deps first:

```bash
pip install -r requirements-rl.txt
python -m rl.train_ppo --timesteps 500000 --n-envs 8
python -m rl.eval --model ppo_pacman --episodes 50
python -m rl.play --model ppo_pacman          # watch it play in the pygame window
```

CPU is fine — at a 20×15 board the bottleneck is env stepping, not the
network. TensorBoard logs land in `./tb/`.

## Vibe

If you find a bug, it's a feature. If you find a feature, it's probably a bug. Contributions welcome but emotionally optional.
