"""Evaluate a trained PPO agent on PacmanEnv.

Usage:
    python -m rl.eval [--model ppo_pacman] [--episodes 50] [--seed 123]
"""
import argparse

import numpy as np


def main():
    from stable_baselines3 import PPO

    from game.gym_env import PacmanEnv

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="ppo_pacman")
    parser.add_argument("--episodes", type=int, default=50)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args()

    model = PPO.load(args.model, device="cpu")
    returns = []
    wins = 0
    for ep in range(args.episodes):
        env = PacmanEnv(seed=args.seed + ep)
        obs, _ = env.reset()
        ep_ret, done = 0.0, False
        while not done:
            action, _ = model.predict(obs, deterministic=args.deterministic)
            obs, r, done, _, _ = env.step(int(action))
            ep_ret += r
        returns.append(ep_ret)
        status = env._game.get_state()["status"]
        if status == "won":
            wins += 1

    returns = np.array(returns)
    print(f"episodes: {args.episodes}")
    print(f"mean return: {returns.mean():.3f} ± {returns.std():.3f}")
    print(f"min / max:   {returns.min():.3f} / {returns.max():.3f}")
    print(f"wins:        {wins} ({100 * wins / args.episodes:.1f}%)")


if __name__ == "__main__":
    main()
