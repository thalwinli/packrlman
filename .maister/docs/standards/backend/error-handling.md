# Error Handling (Project-Specific)

### Prefer built-in exceptions with f-string messages
Raise standard exception types (`RuntimeError`, `ValueError`, `ImportError`) with descriptive f-string messages. Do not introduce a custom exception hierarchy — the project is small and a custom tree would be over-engineering.

```python
raise RuntimeError(f"Could not generate map {width}x{height} with {num_ghosts} ghosts")
```

*Source: game/map_gen.py raise site; 0 custom exception classes across 16 modules. See also global/error-handling.md for general guidance.*
