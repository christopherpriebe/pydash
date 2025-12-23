import tkinter as tk
from pydash.domain.game_state import GameState


class TkCanvasView:
    def __init__(self, root: tk.Tk, *, width: int, height: int) -> None:
        self._w = width
        self._h = height

        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._ground_id = self.canvas.create_rectangle(0, 0, width, 0, outline="", fill="#444")
        self._player_id = self.canvas.create_rectangle(0, 0, 0, 0, outline="", fill="#66f")
        self._text_id = self.canvas.create_text(10, 10, anchor="nw", text="", font=("TkDefaultFont", 12))

    def render_game(self, state: GameState) -> None:
        gy = state.ground_y
        self.canvas.coords(self._ground_id, 0, gy, self._w, self._h)

        p = state.player
        self.canvas.coords(self._player_id, p.x, p.y, p.x + p.size, p.y + p.size)

        # Redraw spikes (simple + fine for now)
        self.canvas.delete("spike")
        for s in state.spikes:
            # Triangle spike in a cell: base on ground, apex up.
            x1, y1 = s.x, s.y + s.size
            x2, y2 = s.x + s.size, s.y + s.size
            x3, y3 = s.x + s.size / 2.0, s.y
            self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill="#f44", outline="", tags=("spike",))

        self.canvas.itemconfigure(
            self._text_id,
            text=f"spikes={len(state.spikes)} y={p.y:.1f} vy={p.vy:.1f}",
        )
