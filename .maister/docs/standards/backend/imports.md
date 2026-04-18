# Import Conventions

### Absolute imports from the package root
All cross-module imports use absolute paths rooted at the top-level package (`game.`, `rl.`). Relative imports (`from .x import ...`) are not used.

```python
from game.core import PacmanGame
from game.types import Action, Status
from game.map_gen import generate_map
```

### PEP 8 import grouping
Imports are grouped into stdlib / third-party / local, separated by blank lines.

```python
import random

import numpy as np

from game.map_gen import generate_map
```

*Source: 9/9 inspected multi-import modules follow both conventions.*
