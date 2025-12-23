from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from pydash.domain.level import Level
from pydash.infra.exceptions import LevelSaveError
from pydash.infra.level_codec import encode_level


@dataclass(frozen=True)
class SaveResult:
    path: Path


class LevelRepository:
    """
    Saves levels into a directory under the current working directory.
    """

    def __init__(self, *, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path.cwd()
        self._levels_dir = self._base_dir / "levels"
        self._levels_dir.mkdir(parents=True, exist_ok=True)

    def save_beaten_level(self, level: Level, beaten_index: int) -> SaveResult:
        """
        beaten_index: 1-based count of levels beaten so far (used for stable filenames).
        """
        filename = f"level_{beaten_index:04d}_v1.json"
        final_path = self._levels_dir / filename
        tmp_path = self._levels_dir / (filename + ".tmp")

        try:
            payload = encode_level(level)
            data = json.dumps(payload, indent=2, sort_keys=True)

            # Atomic-ish write: write temp then replace.
            tmp_path.write_text(data, encoding="utf-8")
            os.replace(tmp_path, final_path)

            return SaveResult(path=final_path)
        except Exception as e:
            # best-effort cleanup
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
            raise LevelSaveError(f"Failed to save level to {final_path}: {e}") from e
