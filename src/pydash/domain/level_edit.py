from __future__ import annotations

from pydash.domain.level import Level
from pydash.domain.level_object import LevelObject


def place_object(level: Level, obj: LevelObject) -> Level:
    # Bounds validation (kept strict and explicit)
    if obj.w <= 0 or obj.h <= 0:
        raise ValueError("w/h must be > 0")
    if obj.x < 0 or obj.x + obj.w > level.length_cells:
        raise ValueError("object out of bounds in x")
    if obj.y < 0 or obj.y + obj.h > level.height_cells:
        raise ValueError("object out of bounds in y")

    # For now enforce “spike is 1 cell”
    if obj.kind == "spike" and (obj.w != 1 or obj.h != 1):
        raise ValueError("spike must be 1x1")

    # Replace any object occupying the same cell (simple “one object per cell” rule for now)
    objs = [o for o in level.objects if not _occupies_cell(o, obj.x, obj.y)]
    objs.append(obj)
    return Level(length_cells=level.length_cells, height_cells=level.height_cells, objects=tuple(objs))


def remove_object_at(level: Level, x: int, y: int) -> Level:
    objs = tuple(o for o in level.objects if not _occupies_cell(o, x, y))
    return Level(length_cells=level.length_cells, height_cells=level.height_cells, objects=objs)


def _occupies_cell(o: LevelObject, x: int, y: int) -> bool:
    return (x >= o.x and x < o.x + o.w and y >= o.y and y < o.y + o.h)
