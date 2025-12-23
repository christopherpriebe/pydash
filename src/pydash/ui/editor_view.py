from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from pydash.domain.level import Level


class EditorView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        canvas_width: int,
        canvas_height: int,
        cell_px: int,
        on_load_clicked: Callable[[], None],
        on_save_clicked: Callable[[], None],
        on_tool_changed: Callable[[str], None],
        on_cell_left_click: Callable[[int, int], None],
        on_cell_right_click: Callable[[int, int], None],
        on_play_clicked: Callable[[], None],
    ) -> None:
        super().__init__(master)

        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._cell_px = cell_px

        # Top bar
        bar = tk.Frame(self)
        bar.pack(side="top", fill="x")

        tk.Button(bar, text="Load…", command=on_load_clicked).pack(side="left", padx=4, pady=4)
        tk.Button(bar, text="Save…", command=on_save_clicked).pack(side="left", padx=4, pady=4)
        tk.Button(bar, text="Play ▶", command=on_play_clicked).pack(side="left", padx=4, pady=4)

        tk.Label(bar, text="Tool:").pack(side="left", padx=(12, 4))
        self._tool_var = tk.StringVar(value="spike")
        tk.OptionMenu(
            bar,
            self._tool_var,
            "spike",
            "solid",
            command=lambda v: on_tool_changed(str(v)),
        ).pack(side="left")

        self._status = tk.Label(bar, text="", anchor="w")
        self._status.pack(side="left", fill="x", expand=True, padx=12)

        # Canvas
        self.canvas = tk.Canvas(
            self,
            width=self._canvas_width,
            height=self._canvas_height,
            highlightthickness=0,
        )
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Button-1>", lambda e: self._handle_click(e.x, e.y, on_cell_left_click))
        self.canvas.bind("<Button-3>", lambda e: self._handle_click(e.x, e.y, on_cell_right_click))
        self.canvas.bind("<Control-Button-1>", lambda e: self._handle_click(e.x, e.y, on_cell_right_click))

    def set_status(self, text: str) -> None:
        self._status.config(text=text)

    def render(self, level: Level) -> None:
        self.canvas.delete("all")

        cols = level.length_cells
        rows = level.height_cells
        cell = self._cell_px

        # Grid
        for c in range(cols + 1):
            x = c * cell
            self.canvas.create_line(x, 0, x, rows * cell)
        for r in range(rows + 1):
            y = r * cell
            self.canvas.create_line(0, y, cols * cell, y)

        # Objects
        for o in level.objects:
            x1 = o.x * cell
            y1 = o.y * cell
            x2 = (o.x + o.w) * cell
            y2 = (o.y + o.h) * cell

            if o.kind == "solid":
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="#999")
            elif o.kind == "spike":
                self.canvas.create_polygon(
                    x1, y2,
                    x2, y2,
                    (x1 + x2) / 2.0, y1,
                    outline="",
                    fill="#f44",
                )
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#0a0", fill="")

    def _handle_click(self, px: int, py: int, cb: Callable[[int, int], None]) -> None:
        cell = self._cell_px
        x = px // cell
        y = py // cell
        cb(int(x), int(y))
