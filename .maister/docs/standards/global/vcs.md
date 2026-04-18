# Version Control Standards

### .gitignore scope
Python bytecode, pytest/coverage caches, virtualenvs, IDE folders, and RL training artifacts must not be committed. Trained model checkpoints (`ppo_pacman*.zip`, `*.zip`), TensorBoard logs (`tb/`), and `runs/` are explicitly excluded. Per-user Claude Code settings (`.claude/settings.local.json`) are also gitignored — never commit machine-local agent configuration.
*Source: C:/Code/packrlman/.gitignore.*
