"""Train a PPO agent on PacmanEnv.

Usage:
    python -m rl.train_ppo [--timesteps 500000] [--n-envs 8] [--save ppo_pacman]
"""
import argparse
from pathlib import Path


def main():
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
    from stable_baselines3.common.monitor import Monitor

    from game.gym_env import PacmanEnv

    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--save", type=str, default="ppo_pacman")
    parser.add_argument("--tb", type=str, default="./tb/")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    def make_env(rank: int):
        def _init():
            return Monitor(PacmanEnv(seed=args.seed + rank))
        return _init

    vec_cls = SubprocVecEnv if args.n_envs > 1 else DummyVecEnv
    envs = vec_cls([make_env(i) for i in range(args.n_envs)])

    model = PPO(
        "CnnPolicy",
        envs,
        verbose=1,
        tensorboard_log=args.tb,
        n_steps=256,
        batch_size=256,
        learning_rate=3e-4,
        device="cpu",
        seed=args.seed,
    )
    model.learn(total_timesteps=args.timesteps, progress_bar=True)

    out = Path(args.save).with_suffix(".zip")
    model.save(out.with_suffix(""))
    print(f"saved to {out}")


if __name__ == "__main__":
    main()
