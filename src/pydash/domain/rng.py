from __future__ import annotations
from typing import Protocol


class RandomSource(Protocol):
    def random(self) -> float:  # returns in [0.0, 1.0)
        ...
