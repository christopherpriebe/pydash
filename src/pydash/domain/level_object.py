from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LevelObject:
    """
    Extensible “object spec” stored in a level.
    Coordinates and sizes are in grid cells.
    """
    kind: str                 # e.g. "solid", "spike"
    x: int                    # cell coordinates
    y: int
    w: int = 1                # size in cells
    h: int = 1
    props: dict[str, Any] = field(default_factory=dict)  # extensible per-object properties
