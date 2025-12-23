from __future__ import annotations

from pydash.domain.level import Level
from pydash.infra.exceptions import LevelDecodeError, LevelEncodeError


_FORMAT = "pydash.level"
_VERSION = 1


def encode_level(level: Level) -> dict:
    try:
        return {
            "format": _FORMAT,
            "version": _VERSION,
            "length_cells": int(level.length_cells),
            "spike_cells": list(level.spike_cells),
        }
    except Exception as e:
        raise LevelEncodeError(f"Failed to encode level: {e}") from e


def decode_level(obj: dict) -> Level:
    try:
        if obj.get("format") != _FORMAT:
            raise LevelDecodeError("Invalid level format marker.")
        if obj.get("version") != _VERSION:
            raise LevelDecodeError("Unsupported level version.")

        length_cells = int(obj["length_cells"])
        if length_cells != 50:
            raise LevelDecodeError("length_cells must be 50 for now.")

        spike_cells_raw = obj.get("spike_cells", [])
        if not isinstance(spike_cells_raw, list):
            raise LevelDecodeError("spike_cells must be a list.")

        spike_cells: list[int] = []
        seen: set[int] = set()
        for x in spike_cells_raw:
            if not isinstance(x, int):
                raise LevelDecodeError("spike_cells entries must be integers.")
            if x < 0 or x >= length_cells:
                raise LevelDecodeError("spike_cells entry out of range.")
            if x in seen:
                raise LevelDecodeError("spike_cells must not contain duplicates.")
            seen.add(x)
            spike_cells.append(x)

        return Level(length_cells=length_cells, spike_cells=tuple(spike_cells))
    except LevelDecodeError:
        raise
    except Exception as e:
        raise LevelDecodeError(f"Failed to decode level: {e}") from e
