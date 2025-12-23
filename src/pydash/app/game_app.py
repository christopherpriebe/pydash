import tkinter as tk

from pydash.app.game_loop import GameLoop
from pydash.domain.game_state import GameState, Player
from pydash.domain.world import World
from pydash.ui.input_mapper import TkInputMapper
from pydash.ui.tk_canvas_view import TkCanvasView


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GD Clone (Skeleton)")

        self.view = TkCanvasView(self.root, width=800, height=450)
        self.input = TkInputMapper(self.root)

        self.world = World()

        # Initial domain state (flat level)
        self.state = GameState(
            player=Player(x=120.0, y=0.0, vy=0.0, size=32.0, on_ground=False),
            ground_y=380.0,
            gravity=2000.0,        # px/s^2 (tune later)
            jump_velocity=-700.0,  # px/s (negative = up)
        )

        # Fixed-step simulation config
        self._fixed_dt = 1.0 / 120.0
        self._accum = 0.0

        self.loop = GameLoop(
            root=self.root,
            render_fn=self._render,
            update_fn=self._update,
            fps=60,
        )

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.loop.start()
        self.root.mainloop()

    def _update(self, dt: float) -> None:
        # Accumulate real time, step world in fixed increments.
        self._accum += dt

        # Sample input once per *render tick*; apply to the next physics step(s).
        inp = self.input.sample()

        # Prevent spiral-of-death if dt spikes.
        max_steps = 5
        steps = 0
        while self._accum >= self._fixed_dt and steps < max_steps:
            self.state = self.world.step(self.state, inp, self._fixed_dt)
            self._accum -= self._fixed_dt
            steps += 1
            # Only allow the press-edge once.
            inp = type(inp)(jump_pressed=False)

    def _render(self) -> None:
        self.view.render_game(self.state)

    def _on_close(self) -> None:
        self.loop.stop()
        self.root.destroy()