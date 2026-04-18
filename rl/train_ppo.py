"""Train a PPO agent on PacmanEnv.

Usage:
    python -m rl.train_ppo [--timesteps 500000] [--n-envs 8] [--save ppo_pacman]
    python -m rl.train_ppo --resume ppo_pacman.zip --timesteps 2000000
"""
import argparse
from pathlib import Path


def main():
    import torch as th
    import torch.nn as nn
    from gymnasium import spaces
    from stable_baselines3 import PPO
    from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
    from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
    from stable_baselines3.common.monitor import Monitor

    from game.gym_env import PacmanEnv

    class SmallCNN(BaseFeaturesExtractor):
        def __init__(self, observation_space: spaces.Box, features_dim: int = 128):
            super().__init__(observation_space, features_dim)
            c, h, w = observation_space.shape
            self.cnn = nn.Sequential(
                nn.Conv2d(c, 16, kernel_size=3, padding=1), nn.ReLU(),
                nn.Conv2d(16, 32, kernel_size=3, padding=1), nn.ReLU(),
                nn.Flatten(),
            )
            with th.no_grad():
                flat = self.cnn(th.zeros(1, c, h, w)).shape[1]
            self.linear = nn.Sequential(nn.Linear(flat, features_dim), nn.ReLU())

        def forward(self, obs: th.Tensor) -> th.Tensor:
            return self.linear(self.cnn(obs))

    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--save", type=str, default="ppo_pacman")
    parser.add_argument("--tb", type=str, default="./tb/")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to saved PPO .zip to continue training from")
    args = parser.parse_args()

    def make_env(rank: int):
        def _init():
            return Monitor(PacmanEnv(seed=args.seed + rank))
        return _init

    vec_cls = SubprocVecEnv if args.n_envs > 1 else DummyVecEnv
    envs = vec_cls([make_env(i) for i in range(args.n_envs)])

    if args.resume:
        resume_path = Path(args.resume)
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume checkpoint not found: {resume_path}")
        print(f"resuming from {resume_path}")
        model = PPO.load(resume_path, env=envs, tensorboard_log=args.tb, device="cpu")
    else:
        model = PPO(
            "MlpPolicy",
            envs,
            policy_kwargs=dict(
                features_extractor_class=SmallCNN,
                features_extractor_kwargs=dict(features_dim=128),
            ),
            verbose=1,
            tensorboard_log=args.tb,
            n_steps=256,
            batch_size=256,
            learning_rate=3e-4,
            device="cpu",
            seed=args.seed,
        )
    model.learn(
        total_timesteps=args.timesteps,
        reset_num_timesteps=not args.resume,
        progress_bar=True,
    )

    out = Path(args.save).with_suffix(".zip")
    model.save(out.with_suffix(""))
    print(f"saved to {out}")


if __name__ == "__main__":
    main()
