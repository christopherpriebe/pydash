from __future__ import annotations

from pydash.domain.exceptions import LevelCompleted, PlayerDied
from pydash.domain.game_state import GameState, Player, Spike
from pydash.domain.input_state import InputState


class World:
    def step(self, state: GameState, inp: InputState, dt: float) -> GameState:
        # ---- Player vertical physics ----
        p = state.player
        if inp.jump_pressed and p.on_ground:
            p = Player(x=p.x, y=p.y, vy=state.jump_velocity, size=p.size, on_ground=False)

        vy = p.vy + state.gravity * dt
        y = p.y + vy * dt

        ground_top = state.ground_y - p.size
        if y >= ground_top:
            y = ground_top
            vy = 0.0
            on_ground = True
        else:
            on_ground = False

        p2 = Player(x=p.x, y=y, vy=vy, size=p.size, on_ground=on_ground)

        # ---- Scroll level left by moving spikes ----
        dx = state.scroll_speed * dt
        moved_spikes = tuple(Spike(x=s.x - dx, y=s.y, size=s.size) for s in state.spikes)

        # ---- Progress ----
        level_scrolled = state.level_scrolled + dx

        # Win when the end of the level passes the player.
        level_length_px = state.level.length_cells * state.cell_size
        level_end_x = state.level_start_x + level_length_px
        # after scrolling, end is at (level_end_x - level_scrolled)
        if (level_end_x - level_scrolled) <= p2.x:
            raise LevelCompleted()

        # ---- Collision ----
        if self._player_hits_any_spike(p2, moved_spikes):
            raise PlayerDied()

        return GameState(
            player=p2,
            ground_y=state.ground_y,
            gravity=state.gravity,
            jump_velocity=state.jump_velocity,
            scroll_speed=state.scroll_speed,
            cell_size=state.cell_size,
            level=state.level,
            level_start_x=state.level_start_x,
            level_scrolled=level_scrolled,
            spikes=moved_spikes,
        )

    def _player_hits_any_spike(self, p: Player, spikes: tuple[Spike, ...]) -> bool:
        px1, py1 = p.x, p.y
        px2, py2 = p.x + p.size, p.y + p.size
        for s in spikes:
            sx1, sy1 = s.x, s.y
            sx2, sy2 = s.x + s.size, s.y + s.size
            if (px1 < sx2 and px2 > sx1 and py1 < sy2 and py2 > sy1):
                return True
        return False
