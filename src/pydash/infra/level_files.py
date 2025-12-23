from __future__ import annotations

import json
import os
from pathlib import Path

from pydash.domain.level import Level
from pydash.infra.exceptions import LevelDecodeError, LevelSaveError
from pydash.infra.level_codec import decode_level, encode_level


def load_level_from_path(path: Path) -> Level:
    try:
        data = path.read_text(encoding="utf-8")
        obj = json.loads(data)
        return decode_level(obj)
    except LevelDecodeError:
        raise
    except Exception as e:
        raise LevelDecodeError(f"Failed to load level from {path}: {e}") from e


def save_level_to_path(level: Level, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        payload = encode_level(level)
        text = json.dumps(payload, indent=2, sort_keys=True)
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except Exception as e:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        raise LevelSaveError(f"Failed to save level to {path}: {e}") from e
