from __future__ import annotations
from dataclasses import dataclass
from pydash.domain.level_object import LevelObject
from pydash.domain.rng import RandomSource


@dataclass(frozen=True)
class Level:
    length_cells: int
    height_cells: int              # lets us validate y; keep simple now
    objects: tuple[LevelObject, ...]


def generate_level(rng: RandomSource, *, length_cells: int = 50, height_cells: int = 14) -> Level:
    # For now: mostly spikes on the ground row.
    # You can later add platforms/blocks probabilistically.
    spike_prob = 0.15
    safe_prefix = 3
    ground_y = height_cells - 1  # bottom row

    objs: list[LevelObject] = []

    for x in range(length_cells):
        if x < safe_prefix:
            continue
        if rng.random() < spike_prob:
            objs.append(LevelObject(kind="spike", x=x, y=ground_y))

    # Optional: add a couple simple blocks to jump on (1x1 or 2x1)
    if rng.random() < 0.6:
        bx = min(length_cells - 4, safe_prefix + 5)
        objs.append(LevelObject(kind="solid", x=bx, y=ground_y - 2, w=2, h=1))

    return Level(length_cells=length_cells, height_cells=height_cells, objects=tuple(objs))
