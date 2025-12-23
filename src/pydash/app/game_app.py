import random
import tkinter as tk

from pydash.app.game_loop import GameLoop
from pydash.domain.exceptions import LevelCompleted, PlayerDied
from pydash.domain.level_object import LevelObject
from pydash.domain.game_state import GameState, Player, Spike, SolidBlock
from pydash.domain.level import Level, generate_level
from pydash.domain.world import World
from pydash.infra.level_repository import LevelRepository
from pydash.infra.exceptions import LevelSaveError
from pydash.ui.input_mapper import TkInputMapper
from pydash.ui.tk_canvas_view import TkCanvasView


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GD Clone (Level + Saving)")

        self.view = TkCanvasView(self.root, width=800, height=450)
        self.input = TkInputMapper(self.root)

        self.world = World()
        self.rng = random.Random()
        self.level_repo = LevelRepository()

        self.levels_beaten = 0

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
        level_start_x = 820.0

        spikes: list[Spike] = []
        solids: list[SolidBlock] = []

        for obj in level.objects:
            x_px = level_start_x + obj.x * cell
            y_px = (ground_y - cell) - (level.height_cells - 1 - obj.y) * cell
            # Note: obj.y is grid row; we map it so obj.y==height-1 sits on ground.

            if obj.kind == "spike":
                spikes.append(Spike(x=x_px, y=y_px, size=cell))
            elif obj.kind == "solid":
                solids.append(SolidBlock(x=x_px, y=y_px, w=obj.w * cell, h=obj.h * cell))
            else:
                # Unknown kinds are ignored by the game for now (but can still be saved/loaded).
                pass

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
            solids=tuple(solids),
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
                # Save beaten level, then advance to a new one
                self.levels_beaten += 1
                try:
                    self.level_repo.save_beaten_level(self.state.level, self.levels_beaten)
                except LevelSaveError:
                    # For now: fail fast (matches your current loop behavior philosophy).
                    # Later: show dialog + continue.
                    raise

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
