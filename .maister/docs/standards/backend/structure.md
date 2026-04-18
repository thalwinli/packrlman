# Module Structure

### Constants at the top of the file
Module-level constants appear directly after imports and before any class/function definition. Keep them sorted by related group (timing, reward, geometry, etc.).

### `main()` + entry-point guard for runnable scripts
Executable scripts define a `main()` function and guard execution with `if __name__ == "__main__": main()`. Argument parsing lives inside `main()`, not at module scope.

```python
def main() -> None:
    args = _parse_args()
    ...

if __name__ == "__main__":
    main()
```

*Source: 4/4 runnable scripts — main.py, rl/train_ppo.py, rl/eval.py, rl/play.py.*
