import random
import tkinter as tk

from pydash.app.game_loop import GameLoop
from pydash.domain.exceptions import LevelCompleted, PlayerDied
from pydash.domain.game_state import GameState, Player, Spike
from pydash.domain.level import Level, generate_level
from pydash.domain.world import World
from pydash.ui.input_mapper import TkInputMapper
from pydash.ui.tk_canvas_view import TkCanvasView


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GD Clone (Level Slice)")

        self.view = TkCanvasView(self.root, width=800, height=450)
        self.input = TkInputMapper(self.root)

        self.world = World()
        self.rng = random.Random()

        self._fixed_dt = 1.0 / 120.0
        self._accum = 0.0

        self.level = generate_level(self.rng, length_cells=50)
        self.state = self._state_from_level(self.level)

        self.loop = GameLoop(
            root=self.root,
            render_fn=self._render,
            update_fn=self._update,
            fps=60,
        )
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _state_from_level(self, level: Level) -> GameState:
        cell = 32.0
        ground_y = 380.0

        player = Player(x=120.0, y=0.0, vy=0.0, size=cell, on_ground=False)

        # Put the start of the level just off-screen to the right.
        level_start_x = 820.0

        # Build spike instances in world coords aligned to the grid.
        spikes: list[Spike] = []
        for i in level.spike_cells:
            x = level_start_x + i * cell
            y = ground_y - cell
            spikes.append(Spike(x=x, y=y, size=cell))

        return GameState(
            player=player,
            ground_y=ground_y,
            gravity=2000.0,
            jump_velocity=-700.0,
            scroll_speed=260.0,
            cell_size=cell,
            level=level,
            level_start_x=level_start_x,
            level_scrolled=0.0,
            spikes=tuple(spikes),
        )

    def run(self) -> None:
        self.loop.start()
        self.root.mainloop()

    def _update(self, dt: float) -> None:
        self._accum += dt
        inp = self.input.sample()

        max_steps = 5
        steps = 0
        while self._accum >= self._fixed_dt and steps < max_steps:
            try:
                self.state = self.world.step(self.state, inp, self._fixed_dt)
            except PlayerDied:
                # Restart SAME level
                self.state = self._state_from_level(self.state.level)
                self._accum = 0.0
                break
            except LevelCompleted:
                # New level
                self.level = generate_level(self.rng, length_cells=50)
                self.state = self._state_from_level(self.level)
                self._accum = 0.0
                break

            self._accum -= self._fixed_dt
            steps += 1
            inp = type(inp)(jump_pressed=False)

    def _render(self) -> None:
        self.view.render_game(self.state)

    def _on_close(self) -> None:
        self.loop.stop()
        self.root.destroy()
