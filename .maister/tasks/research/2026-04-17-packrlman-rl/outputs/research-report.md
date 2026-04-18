# Using packrlman as a Deep RL Environment

**Date**: 2026-04-17
**Scope**: Practical roadmap for training RL agents on the existing packrlman game.

---

## 1. What the codebase already gives you

You got lucky — the environment is already 80% RL-ready.

| Need | Where it lives | Status |
|------|----------------|--------|
| Discrete action space (5 actions) | `game.types.Action` (UP/DOWN/LEFT/RIGHT/NOOP) | ✅ ready |
| Atomic `step(action) → (state, reward, done)` | `PacmanGame.step` in `game/core.py:69` | ✅ ready |
| Reset semantics | `PacmanGame.reset()` | ✅ ready |
| Deterministic, seedable | `random.Random(seed)` threaded through map gen + ghost moves | ✅ ready |
| Reward shaping | `DOT_REWARD=1.0`, `WIN_BONUS=10`, `LOSS_PENALTY=10`, `TIME_PENALTY=0.01` | ✅ ready |
| Tensor observation | `PacmanGame.to_tensor()` → `(4, H, W)` float32 | ✅ ready |
| Headless core (no pygame) | Enforced by `test_core_imports_without_pygame` | ✅ ready — critical for training throughput |

**Gap**: it isn't a `gymnasium.Env` yet. That's ~40 lines of glue.

---

## 2. Algorithms worth trying (ranked by fit)

### Tier 1 — Start here

**DQN (Deep Q-Network)**
- Classical choice for discrete-action pixel/grid envs. Atari-scale problem, your env is smaller.
- Use **Double DQN + Dueling DQN + Prioritized Experience Replay** together — these are well-studied upgrades with clean implementations.
- Expected training time on CPU: minutes to ~1 hour to reach competent play on a 20×15 board.

**PPO (Proximal Policy Optimization)**
- On-policy actor-critic. Very robust out of the box — works with almost no hyperparameter tuning.
- Often trains faster in wall-clock time than DQN on small envs because of parallel env rollouts.
- Recommended if you only want to try one algorithm.

### Tier 2 — Once Tier 1 works

- **A2C / A3C** — simpler than PPO, older; useful for comparison.
- **Rainbow DQN** — DQN + 6 improvements stacked. Strongest value-based method; more moving parts.
- **IMPALA** — if you want to scale to many parallel envs.

### Tier 3 — Advanced/research

- **Muzero / EfficientZero** — model-based, strong sample efficiency. Overkill for a hobby project but good learning exercise.
- **Decision Transformer / offline RL** — if you want to try a dataset-based approach.

**Recommendation**: **start with PPO using Stable-Baselines3**. It's the "just works" option. Move to DQN only if you want to study value-based methods specifically.

---

## 3. Libraries & tools

### Core (pick one stack)

**Stack A — Highest-level, easiest (recommended)**
```
gymnasium              # env API (the successor to OpenAI gym)
stable-baselines3      # PPO, DQN, A2C, SAC implementations
torch                  # SB3 backend
tensorboard            # training curves
```
Install: `pip install gymnasium stable-baselines3[extra] torch tensorboard`

**Stack B — Middle-level, more control**
```
gymnasium
cleanrl                # single-file reference implementations (great to learn from)
torch
wandb                  # or tensorboard
```

**Stack C — Research-grade**
```
gymnasium
torchrl OR rllib       # modular, scale to distributed
```

### Supporting
- `numpy` (already in `requirements.txt`)
- `matplotlib` / `tensorboard` for training curves
- `imageio` if you want to record gameplay videos

---

## 4. Input, output, and data flow

### Observation (input to the network)

You already have the right shape: `PacmanGame.to_tensor()` returns `(4, H, W) float32`.

Channels:
- 0: walls (binary)
- 1: dots (binary)
- 2: player (one-hot)
- 3: ghosts (count — may be >1 if overlap)

This maps directly onto a small **CNN** (think Nature DQN architecture, scaled down):

```
Input: (4, 15, 20)
Conv2d(4→16, kernel=3, padding=1) + ReLU
Conv2d(16→32, kernel=3, padding=1) + ReLU
Flatten → Linear(32·15·20 → 128) + ReLU
Linear(128 → 5)   # Q-values, or policy logits + value head
```

A 2-3 layer CNN + 1 FC is plenty for a 20×15 board.

### Optional: flat observation for an MLP baseline

For the smallest possible experiment, flatten the tensor to length `4*H*W = 1200` and use a 2-layer MLP. Trains faster, caps at slightly lower performance.

### Action (output of the network)

Discrete, 5 actions (match `Action` enum). Output either:
- **DQN**: 5 Q-values → `argmax` at inference, ε-greedy during training
- **PPO**: 5 policy logits (softmax) + 1 scalar value estimate

### Reward signal

Already shaped in `game/core.py:22-26`. Reasonable defaults. Things you may want to tune:
- `TIME_PENALTY=0.01` pushes the agent to finish quickly — good.
- `DOT_REWARD=1.0` vs `WIN_BONUS=10.0` — if the agent gets stuck after eating most dots, increase `WIN_BONUS`.
- Consider adding a **shaped ghost-distance penalty** if the agent never learns to evade. Be careful — shaped rewards can create unintended behaviors.

### Episodes & data

- Each episode = one call to `reset()` through `done=True`.
- On random policy a 20×15 board typically ends in < 200 steps (ghost collision).
- Training data comes from **experience replay** (DQN) or **on-policy rollouts** (PPO). You do not supply data — the agent generates it by playing.

**Sample budget** (rough, 20×15 board, 3 ghosts):
- PPO: ~**100K–500K env steps** to reach "noticeably better than random" (eats most dots, avoids immediate collisions).
- PPO: ~**1M–5M env steps** for good play.
- DQN: similar sample budget but more wall-clock because no parallel envs by default.
- On a modern CPU with 8 parallel envs: 100K steps ≈ minutes, 1M ≈ ~1 hour.

---

## 5. Expected results

**Realistic**
- Agent learns to move toward dots consistently ✓
- Agent learns to flee from adjacent ghosts ✓
- Agent completes episodes (wins) on easy configs (`wall_density=0.15`, 1-2 ghosts) ✓
- Generalization across random seeds on a fixed board size ✓

**Harder (needs more training / tuning)**
- Consistent wins with 3+ ghosts on default board — possible but finicky.
- Generalization across **board sizes** — needs architecture that doesn't hardcode shape (e.g., global average pool instead of flatten).
- Long-horizon planning (e.g., "corner the ghost cluster before going for the last dot") — PPO struggles; model-based methods or curriculum help.

**What won't work out of the box**
- Pre-trained Atari Pacman policies (different action space, different dynamics, different obs).
- Copy-pasting Atari hyperparameters wholesale — your env is smaller, so smaller networks and shorter replay buffers are better.

---

## 6. Step-by-step plan

### Step 1 — Add the gymnasium wrapper (1 file, ~40 LOC)
Create `game/gym_env.py`:
```python
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from game.core import PacmanGame
from game.types import Action

class PacmanEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, width=20, height=15, wall_density=0.25, num_ghosts=3, seed=None):
        super().__init__()
        self._game = PacmanGame(width, height, wall_density, num_ghosts, seed)
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=0.0, high=np.inf, shape=(4, height, width), dtype=np.float32
        )

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self._game = PacmanGame(
                self._game._width, self._game._height,
                self._game._wall_density, self._game._num_ghosts, seed
            )
        else:
            self._game.reset()
        return self._game.to_tensor(), {}

    def step(self, action):
        _, reward, done = self._game.step(Action(action))
        obs = self._game.to_tensor()
        return obs, reward, done, False, {}   # (obs, reward, terminated, truncated, info)
```

Keep this module pygame-free (same invariant as the rest of `game/core.py` & friends).

### Step 2 — Sanity-check the env
```python
from stable_baselines3.common.env_checker import check_env
check_env(PacmanEnv())
```
Fix any shape/dtype complaints before training.

### Step 3 — Train a PPO baseline (~50 LOC script)
```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from game.gym_env import PacmanEnv

def make_env(seed):
    return lambda: PacmanEnv(seed=seed)

envs = SubprocVecEnv([make_env(i) for i in range(8)])
model = PPO("CnnPolicy", envs, verbose=1, tensorboard_log="./tb/",
            n_steps=256, batch_size=256, learning_rate=3e-4)
model.learn(total_timesteps=500_000)
model.save("ppo_pacman")
```
Monitor in TensorBoard: `tensorboard --logdir ./tb/`.

### Step 4 — Evaluate
```python
import numpy as np
env = PacmanEnv(seed=123)
model = PPO.load("ppo_pacman")
returns = []
for _ in range(50):
    obs, _ = env.reset()
    ep_ret, done = 0.0, False
    while not done:
        a, _ = model.predict(obs, deterministic=True)
        obs, r, done, _, _ = env.step(int(a))
        ep_ret += r
    returns.append(ep_ret)
print("mean return:", np.mean(returns), "±", np.std(returns))
```

### Step 5 — Visualize (optional, reuse pygame shell)
Render the trained policy with the existing pygame app — replace `pending_action` with `model.predict(game.to_tensor())`. One branch, ~20 LOC change in `game/pygame_app.py` or a new `game/pygame_replay.py`.

### Step 6 — Iterate
- Try DQN via SB3 with the same env to compare.
- Curriculum: start `num_ghosts=1, wall_density=0.1`, ramp up as reward plateaus.
- Add a channel to `to_tensor()` for tick/step count if time-awareness matters.
- Once wall-clock matters, follow the I1/I2 suggestions from the earlier code review: pre-allocate the observation buffer in `PacmanEnv.__init__` and pass it into a new `to_tensor(out=buf)` variant.

---

## 7. Pitfalls specific to packrlman

1. **Deterministic-but-fixed map bias.** `PacmanGame(seed=X)` gives the same map every reset. SB3 will happily overfit. **Fix**: let `reset()` re-sample the map with a fresh seed each episode (easy — call `PacmanGame.__init__` with a new seed per reset, or modify `reset()` in core to regenerate).
2. **Observation copy overhead.** `get_state()` deep-copies sets; `to_tensor()` allocates a fresh array every call. For RL throughput this matters. See code-review I1/I2.
3. **Ghost policy was just changed to be stickier with a 0.2 turn probability.** That's fine for RL — just be aware the environment dynamics changed from the initial commit. Make sure your baseline was trained against the current behavior.
4. **`get_state()` vs `to_tensor()`.** Use `to_tensor()` in the RL loop — it's the allocation-light path and the right shape.
5. **Variable-size boards.** A CNN with a `Flatten → Linear` bottleneck locks you to one `(H, W)`. If you want size generalization later, swap to `AdaptiveAvgPool2d` before the FC head.

---

## 8. Minimum viable milestones

| Milestone | Effort | Signal |
|-----------|--------|--------|
| Gym wrapper passes `check_env` | 1 hr | Env is valid |
| Random-policy baseline (mean return) | 15 min | Establishes floor |
| PPO trains for 100K steps | 30 min | Sanity |
| PPO beats random by 2× mean return | ~1 hr wall-clock | Learning works |
| PPO wins episodes on easy config | evening project | RL loop validated |
| DQN vs PPO comparison | weekend | Nice writeup |
| Curriculum + size generalization | multi-evening | Real project |

---

## 9. Further reading (by relevance)

- **Spinning Up in Deep RL** (OpenAI) — the best single resource for algorithm intuition. https://spinningup.openai.com
- **CleanRL** — single-file readable implementations of PPO/DQN you can crib from. https://github.com/vwxyzjn/cleanrl
- **Stable-Baselines3 docs** — https://stable-baselines3.readthedocs.io
- **Gymnasium docs** — https://gymnasium.farama.org
- Mnih et al., 2015, *Human-level control through deep reinforcement learning* (the Nature DQN paper) — the architecture baseline for grid/pixel obs.
- Schulman et al., 2017, *Proximal Policy Optimization Algorithms* — PPO paper.

---

## TL;DR

1. Add `game/gym_env.py` as a gymnasium wrapper around `PacmanGame` (~40 LOC).
2. `pip install gymnasium stable-baselines3[extra] torch tensorboard`.
3. Train PPO with a small CNN policy on 8 parallel envs for ~500K–1M steps.
4. Make `reset()` re-sample the map so you don't overfit.
5. Expect competent play (eats dots, avoids ghosts) in <1 hr CPU wall-clock.
6. Iterate: curriculum, DQN comparison, size generalization.
