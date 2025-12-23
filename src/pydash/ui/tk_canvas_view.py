import tkinter as tk
from pydash.domain.game_state import GameState


class TkCanvasView:
    def __init__(self, root: tk.Tk, *, width: int, height: int) -> None:
        self._w = width
        self._h = height

        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Ground (persistent)
        self._ground_id = self.canvas.create_rectangle(
            0, 0, width, 0, outline="", fill="#444"
        )

        # Player (persistent)
        self._player_id = self.canvas.create_rectangle(
            0, 0, 0, 0, outline="", fill="#66f"
        )

        # Debug text (optional)
        self._text_id = self.canvas.create_text(
            10, 10, anchor="nw", text="", font=("TkDefaultFont", 12)
        )

    def render_game(self, state: GameState) -> None:
        # Ground rectangle from ground_y to bottom
        gy = state.ground_y
        self.canvas.coords(self._ground_id, 0, gy, self._w, self._h)

        # Player as axis-aligned square
        p = state.player
        x1 = p.x
        y1 = p.y
        x2 = p.x + p.size
        y2 = p.y + p.size
        self.canvas.coords(self._player_id, x1, y1, x2, y2)

        self.canvas.itemconfigure(
            self._text_id,
            text=f"y={p.y:.1f} vy={p.vy:.1f} on_ground={p.on_ground}",
        )