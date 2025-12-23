from __future__ import annotations

from typing import Any

from pydash.domain.level import Level
from pydash.domain.level_object import LevelObject
from pydash.infra.exceptions import LevelDecodeError, LevelEncodeError


_FORMAT = "pydash.level"
_VERSION_LATEST = 2


def encode_level(level: Level) -> dict:
    try:
        return {
            "format": _FORMAT,
            "version": _VERSION_LATEST,
            "length_cells": int(level.length_cells),
            "height_cells": int(level.height_cells),
            "objects": [
                {
                    "kind": o.kind,
                    "x": int(o.x),
                    "y": int(o.y),
                    "w": int(o.w),
                    "h": int(o.h),
                    "props": dict(o.props),
                }
                for o in level.objects
            ],
        }
    except Exception as e:
        raise LevelEncodeError(f"Failed to encode level: {e}") from e


def decode_level(obj: dict) -> Level:
    try:
        if obj.get("format") != _FORMAT:
            raise LevelDecodeError("Invalid level format marker.")

        ver = obj.get("version")
        if ver == 1:
            return _decode_v1(obj)
        if ver == 2:
            return _decode_v2(obj)

        raise LevelDecodeError("Unsupported level version.")
    except LevelDecodeError:
        raise
    except Exception as e:
        raise LevelDecodeError(f"Failed to decode level: {e}") from e


def _decode_v2(obj: dict) -> Level:
    length_cells = int(obj["length_cells"])
    if length_cells != 50:
        raise LevelDecodeError("length_cells must be 50 for now.")

    height_cells = int(obj.get("height_cells", 14))
    if height_cells <= 0:
        raise LevelDecodeError("height_cells must be positive.")

    raw_objects = obj.get("objects", [])
    if not isinstance(raw_objects, list):
        raise LevelDecodeError("objects must be a list.")

    parsed: list[LevelObject] = []
    for i, ro in enumerate(raw_objects):
        if not isinstance(ro, dict):
            raise LevelDecodeError(f"objects[{i}] must be an object.")

        kind = ro.get("kind")
        if not isinstance(kind, str) or not kind:
            raise LevelDecodeError(f"objects[{i}].kind must be a non-empty string.")

        x = ro.get("x")
        y = ro.get("y")
        w = ro.get("w", 1)
        h = ro.get("h", 1)
        props = ro.get("props", {})

        if not all(isinstance(v, int) for v in (x, y, w, h)):
            raise LevelDecodeError(f"objects[{i}] x/y/w/h must be integers.")
        if w <= 0 or h <= 0:
            raise LevelDecodeError(f"objects[{i}] w/h must be > 0.")
        if x < 0 or x + w > length_cells:
            raise LevelDecodeError(f"objects[{i}] out of bounds in x.")
        if y < 0 or y + h > height_cells:
            raise LevelDecodeError(f"objects[{i}] out of bounds in y.")
        if not isinstance(props, dict):
            raise LevelDecodeError(f"objects[{i}].props must be an object.")

        # Simple rule: spikes are 1x1 for now (matches “one cell”)
        if kind == "spike" and (w != 1 or h != 1):
            raise LevelDecodeError(f"objects[{i}] spike must be 1x1.")

        parsed.append(LevelObject(kind=kind, x=x, y=y, w=w, h=h, props=props))

    return Level(length_cells=length_cells, height_cells=height_cells, objects=tuple(parsed))


def _decode_v1(obj: dict) -> Level:
    # Old format:
    # { length_cells: 50, spike_cells: [..] }
    length_cells = int(obj["length_cells"])
    if length_cells != 50:
        raise LevelDecodeError("length_cells must be 50 for now.")

    spike_cells = obj.get("spike_cells", [])
    if not isinstance(spike_cells, list) or not all(isinstance(x, int) for x in spike_cells):
        raise LevelDecodeError("spike_cells must be a list of ints.")

    height_cells = 14
    ground_y = height_cells - 1
    objects = tuple(LevelObject(kind="spike", x=x, y=ground_y) for x in spike_cells)
    return Level(length_cells=length_cells, height_cells=height_cells, objects=objects)
