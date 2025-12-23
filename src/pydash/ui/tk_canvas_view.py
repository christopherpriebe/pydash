import tkinter as tk


class TkCanvasView:
    def __init__(self, root: tk.Tk, *, width: int, height: int) -> None:
        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Create a placeholder item once; update it each frame.
        self._text_id = self.canvas.create_text(
            width // 2,
            height // 2,
            text="GD Clone Skeleton Running",
            font=("TkDefaultFont", 18),
        )

    def render_placeholder(self) -> None:
        # You can add more draw calls later; keep it simple for now.
        # Canvas persists items, so we don’t need to recreate them.
        pass
