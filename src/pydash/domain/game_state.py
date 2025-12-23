from __future__ import annotations
from dataclasses import dataclass
from pydash.domain.level import Level


@dataclass(frozen=True)
class Spike:
    x: float
    y: float
    size: float


@dataclass(frozen=True)
class SolidBlock:
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Player:
    x: float
    y: float
    vy: float
    size: float
    on_ground: bool


@dataclass(frozen=True)
class GameState:
    player: Player
    ground_y: float
    gravity: float
    jump_velocity: float

    scroll_speed: float
    cell_size: float

    level: Level
    level_start_x: float
    level_scrolled: float

    spikes: tuple[Spike, ...]
    solids: tuple[SolidBlock, ...]
