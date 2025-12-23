from __future__ import annotations
import tkinter as tk
from pydash.domain.input_state import InputState


class TkInputMapper:
    def __init__(self, root: tk.Tk) -> None:
        self._jump_down = False
        self._jump_pressed_edge = False

        root.bind("<KeyPress-space>", self._on_space_down)
        root.bind("<KeyRelease-space>", self._on_space_up)

        # Helps ensure root gets key events.
        root.focus_set()

    def _on_space_down(self, _evt: tk.Event) -> None:
        if not self._jump_down:
            self._jump_pressed_edge = True
        self._jump_down = True

    def _on_space_up(self, _evt: tk.Event) -> None:
        self._jump_down = False

    def sample(self) -> InputState:
        # “Pressed this frame” semantics.
        pressed = self._jump_pressed_edge
        self._jump_pressed_edge = False
        return InputState(jump_pressed=pressed)
