from __future__ import annotations

from pydash.domain.exceptions import LevelCompleted, PlayerDied
from pydash.domain.game_state import GameState, Player, Spike, SolidBlock
from pydash.domain.input_state import InputState


class World:
    def step(self, state: GameState, inp: InputState, dt: float) -> GameState:
        # ----- Jump -----
        p = state.player
        if inp.jump_pressed and p.on_ground:
            p = Player(x=p.x, y=p.y, vy=state.jump_velocity, size=p.size, on_ground=False)

        # Integrate
        vy = p.vy + state.gravity * dt
        y = p.y + vy * dt

        # ----- Scroll world (move objects left) -----
        dx = state.scroll_speed * dt
        spikes = tuple(Spike(x=s.x - dx, y=s.y, size=s.size) for s in state.spikes)
        solids = tuple(SolidBlock(x=b.x - dx, y=b.y, w=b.w, h=b.h) for b in state.solids)

        level_scrolled = state.level_scrolled + dx

        # ----- Vertical collision: ground + solids -----
        size = p.size
        # candidate floor is ground
        floor_y = state.ground_y - size

        # If falling, allow landing on the top of any solid that overlaps horizontally.
        # Simple & stable for now: only resolve "from above".
        if vy >= 0.0:
            px1, px2 = p.x, p.x + size
            for b in solids:
                bx1, bx2 = b.x, b.x + b.w
                if px1 < bx2 and px2 > bx1:
                    top = b.y - size
                    # If player crossed the top this frame (or is slightly inside), snap to top
                    if y >= top and p.y <= top + 1e-6:
                        if top < floor_y:
                            floor_y = top

        if y >= floor_y:
            y = floor_y
            vy = 0.0
            on_ground = True
        else:
            on_ground = False

        p2 = Player(x=p.x, y=y, vy=vy, size=size, on_ground=on_ground)

        # ----- Win condition -----
        level_length_px = state.level.length_cells * state.cell_size
        level_end_x = state.level_start_x + level_length_px
        if (level_end_x - level_scrolled) <= p2.x:
            raise LevelCompleted()

        # ----- Hazard collision (AABB vs spike cell) -----
        if self._player_hits_any_spike(p2, spikes):
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
            spikes=spikes,
            solids=solids,
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
