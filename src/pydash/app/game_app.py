from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from pydash.app.editor_controller import EditorController
from pydash.app.game_loop import GameLoop
from pydash.domain.exceptions import LevelCompleted, PlayerDied
from pydash.domain.game_state import GameState, Player, Spike, SolidBlock
from pydash.domain.level import Level, generate_level
from pydash.domain.world import World
from pydash.infra.exceptions import LevelSaveError
from pydash.infra.level_repository import LevelRepository
from pydash.ui.editor_view import EditorView
from pydash.ui.input_mapper import TkInputMapper
from pydash.ui.tk_canvas_view import TkCanvasView


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GD Clone")

        # One place for content widgets
        self.content = tk.Frame(self.root)
        self.content.pack(fill="both", expand=True)

        self.input = TkInputMapper(self.root)

        self.world = World()
        self.rng = random.Random()
        self.level_repo = LevelRepository()
        self.levels_beaten = 0

        self._fixed_dt = 1.0 / 120.0
        self._accum = 0.0

        # --- Play view (canvas) ---
        self.play_view = TkCanvasView(self.content, width=800, height=450)

        # --- Editor controller + view ---
        initial_editor_level = generate_level(self.rng, length_cells=50, height_cells=14)
        self.editor = EditorController(initial_editor_level)

        self.editor_view = EditorView(
            self.content,
            canvas_width=800,
            canvas_height=14 * 16,
            cell_px=16,
            on_load_clicked=self._editor_load,
            on_save_clicked=self._editor_save,
            on_play_clicked=self._editor_play,   # ✅ Play button
            on_tool_changed=self._editor_tool_changed,
            on_cell_left_click=self._editor_place,
            on_cell_right_click=self._editor_delete,
        )

        # Menu
        self._install_menu()

        # Start in editor mode
        self._mode = "editor"
        self._show_editor()

        # Loop
        self.loop = GameLoop(
            root=self.root,
            render_fn=self._render,
            update_fn=self._update,
            fps=60,
        )
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _install_menu(self) -> None:
        menubar = tk.Menu(self.root)
        mode_menu = tk.Menu(menubar, tearoff=0)
        mode_menu.add_command(label="Play", command=self._show_play)
        mode_menu.add_command(label="Editor", command=self._show_editor)
        menubar.add_cascade(label="Mode", menu=mode_menu)
        self.root.config(menu=menubar)

    def run(self) -> None:
        self.loop.start()
        self.root.mainloop()

    # ---------- Mode switching ----------

    def _show_play(self) -> None:
        self._mode = "play"
        self.editor_view.pack_forget()
        self.play_view.canvas.pack(fill="both", expand=True)

    def _show_editor(self) -> None:
        self._mode = "editor"
        self.play_view.canvas.pack_forget()
        self.editor_view.pack(fill="both", expand=True)
        self.editor_view.set_status("Left click = place, Right click = delete")
        self.editor_view.render(self.editor.state.level)

    def _editor_play(self) -> None:
        # ✅ “Play this level”: reset run state from editor level and switch
        self.state = self._state_from_level(self.editor.state.level)
        self._accum = 0.0
        self._show_play()

    # ---------- Editor callbacks ----------

    def _editor_tool_changed(self, tool: str) -> None:
        self.editor.set_tool(tool)
        self.editor_view.set_status(f"Tool: {tool} | Left=place Right=delete")

    def _editor_place(self, x: int, y: int) -> None:
        self.editor.click_place(x, y)
        self.editor_view.render(self.editor.state.level)

    def _editor_delete(self, x: int, y: int) -> None:
        self.editor.click_delete(x, y)
        self.editor_view.render(self.editor.state.level)

    def _editor_load(self) -> None:
        path_str = filedialog.askopenfilename(
            title="Load level",
            filetypes=[("Level JSON", "*.json"), ("All files", "*.*")],
        )
        if not path_str:
            return
        self.editor.load_from(Path(path_str))
        self.editor_view.set_status(f"Loaded: {Path(path_str).name}")
        self.editor_view.render(self.editor.state.level)

    def _editor_save(self) -> None:
        path_str = filedialog.asksaveasfilename(
            title="Save level",
            defaultextension=".json",
            filetypes=[("Level JSON", "*.json"), ("All files", "*.*")],
        )
        if not path_str:
            return
        self.editor.save_to(Path(path_str))
        self.editor_view.set_status(f"Saved: {Path(path_str).name}")

    # ---------- Play state construction ----------

    def _state_from_level(self, level: Level) -> GameState:
        cell = 32.0
        ground_y = 380.0

        player = Player(x=120.0, y=0.0, vy=0.0, size=cell, on_ground=False)
        level_start_x = 820.0

        spikes: list[Spike] = []
        solids: list[SolidBlock] = []

        # Map grid y to pixel y so that y == height-1 sits on the ground row
        for obj in level.objects:
            x_px = level_start_x + obj.x * cell
            y_px = (ground_y - cell) - (level.height_cells - 1 - obj.y) * cell

            if obj.kind == "spike":
                spikes.append(Spike(x=x_px, y=y_px, size=cell))
            elif obj.kind == "solid":
                solids.append(SolidBlock(x=x_px, y=y_px, w=obj.w * cell, h=obj.h * cell))

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

    # ---------- Game loop ----------

    def _update(self, dt: float) -> None:
        if self._mode == "editor":
            return

        self._accum += dt
        inp = self.input.sample()

        max_steps = 5
        steps = 0
        while self._accum >= self._fixed_dt and steps < max_steps:
            try:
                self.state = self.world.step(self.state, inp, self._fixed_dt)
            except PlayerDied:
                self.state = self._state_from_level(self.state.level)
                self._accum = 0.0
                break
            except LevelCompleted:
                self.levels_beaten += 1
                try:
                    self.level_repo.save_beaten_level(self.state.level, self.levels_beaten)
                except LevelSaveError:
                    raise

                self.state = self._state_from_level(generate_level(self.rng, length_cells=50, height_cells=14))
                self._accum = 0.0
                break

            self._accum -= self._fixed_dt
            steps += 1
            inp = type(inp)(jump_pressed=False)

    def _render(self) -> None:
        if self._mode == "editor":
            return
        self.play_view.render_game(self.state)

    def _on_close(self) -> None:
        self.loop.stop()
        self.root.destroy()
