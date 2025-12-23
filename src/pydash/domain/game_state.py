from __future__ import annotations
from dataclasses import dataclass
from pydash.domain.level import Level


@dataclass(frozen=True)
class Spike:
    x: float
    y: float
    size: float


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

    # Scrolling / grid
    scroll_speed: float
    cell_size: float

    # Level
    level: Level
    level_start_x: float     # world x where cell 0 begins
    level_scrolled: float    # how far the level has moved left since start (px)

    # Prebuilt spikes for the current run (world coords, moved each step)
    spikes: tuple[Spike, ...]
