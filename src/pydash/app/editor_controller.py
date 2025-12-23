from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydash.domain.level import Level
from pydash.domain.level_edit import place_object, remove_object_at
from pydash.domain.level_object import LevelObject
from pydash.infra.level_files import load_level_from_path, save_level_to_path


@dataclass
class EditorState:
    level: Level
    tool: str  # "spike" | "solid"
    last_path: Path | None = None


class EditorController:
    def __init__(self, initial_level: Level) -> None:
        self.state = EditorState(level=initial_level, tool="spike")

    def set_tool(self, tool: str) -> None:
        if tool not in ("spike", "solid"):
            return
        self.state.tool = tool

    def click_place(self, x: int, y: int) -> None:
        # Ignore out-of-bounds clicks safely
        if x < 0 or x >= self.state.level.length_cells:
            return
        if y < 0 or y >= self.state.level.height_cells:
            return

        obj = LevelObject(kind=self.state.tool, x=x, y=y, w=1, h=1)
        self.state.level = place_object(self.state.level, obj)

    def click_delete(self, x: int, y: int) -> None:
        if x < 0 or x >= self.state.level.length_cells:
            return
        if y < 0 or y >= self.state.level.height_cells:
            return
        self.state.level = remove_object_at(self.state.level, x, y)

    def load_from(self, path: Path) -> None:
        lvl = load_level_from_path(path)
        self.state.level = lvl
        self.state.last_path = path

    def save_to(self, path: Path) -> None:
        save_level_to_path(self.state.level, path)
        self.state.last_path = path
