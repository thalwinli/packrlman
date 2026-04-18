# Dependency Management

### Split core vs. RL dependencies
Runtime/game dependencies live in `requirements.txt` (currently `pygame`, `numpy`). Optional RL training dependencies (`gymnasium`, `stable-baselines3`, `torch`, `tensorboard`) live in `requirements-rl.txt`. The core game must remain installable and runnable without the RL dependencies.

```bash
pip install -r requirements.txt       # play
pip install -r requirements-rl.txt    # train / eval
```

### Pin minimum versions with `>=`
Dependencies use `>=` to pin a known-compatible minimum, not `==` exact pins. No lockfile is in use.

*Source: requirements.txt, requirements-rl.txt.*
