from __future__ import annotations
from pydash.domain.game_state import GameState, Player
from pydash.domain.input_state import InputState


class World:
    def step(self, state: GameState, inp: InputState, dt: float) -> GameState:
        p = state.player

        # Jump: only if on ground and jump was pressed this frame.
        if inp.jump_pressed and p.on_ground:
            p = Player(x=p.x, y=p.y, vy=state.jump_velocity, size=p.size, on_ground=False)

        # Integrate velocity + position (simple Euler)
        vy = p.vy + state.gravity * dt
        y = p.y + vy * dt

        # Ground collision
        ground_top = state.ground_y - p.size
        if y >= ground_top:
            y = ground_top
            vy = 0.0
            on_ground = True
        else:
            on_ground = False

        p2 = Player(x=p.x, y=y, vy=vy, size=p.size, on_ground=on_ground)
        return GameState(
            player=p2,
            ground_y=state.ground_y,
            gravity=state.gravity,
            jump_velocity=state.jump_velocity,
        )
