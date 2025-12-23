from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable


class GameLoop:
    def __init__(
        self,
        *,
        root: tk.Tk,
        update_fn: Callable[[float], None],
        render_fn: Callable[[], None],
        fps: int = 60,
    ) -> None:
        self._root = root
        self._update_fn = update_fn
        self._render_fn = render_fn
        self._target_ms = max(1, int(1000 / max(1, fps)))

        self._running = False
        self._after_id: str | None = None
        self._last_t = 0.0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._last_t = time.monotonic()
        self._schedule_next()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            try:
                self._root.after_cancel(self._after_id)
            except tk.TclError:
                # Root may already be destroyed; ignore during shutdown.
                pass
            finally:
                self._after_id = None

    def _schedule_next(self) -> None:
        self._after_id = self._root.after(self._target_ms, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return

        now = time.monotonic()
        dt = now - self._last_t
        self._last_t = now

        # Clamp to avoid huge dt after pauses/minimize.
        if dt > 0.1:
            dt = 0.1

        try:
            self._update_fn(dt)
            self._render_fn()
        except Exception:
            # For now: fail fast rather than silently corrupt state.
            # Later: log + show error dialog + recover to menu.
            self.stop()
            raise

        self._schedule_next()
