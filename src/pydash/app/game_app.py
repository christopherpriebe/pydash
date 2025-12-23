import tkinter as tk

from pydash.app.game_loop import GameLoop
from pydash.ui.tk_canvas_view import TkCanvasView


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GD Clone (Skeleton)")

        # Keep it explicit: fixed canvas size first; add scaling later.
        self.view = TkCanvasView(self.root, width=800, height=450)

        # Create loop after view exists so it can render.
        self.loop = GameLoop(
            root=self.root,
            render_fn=self._render,
            update_fn=self._update,
            fps=60,
        )

        # Ensure we stop cleanly when the window is closed.
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.loop.start()
        self.root.mainloop()

    def _update(self, dt: float) -> None:
        # Nothing yet — placeholder.
        pass

    def _render(self) -> None:
        self.view.render_placeholder()

    def _on_close(self) -> None:
        self.loop.stop()
        self.root.destroy()
