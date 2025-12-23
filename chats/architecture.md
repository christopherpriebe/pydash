# Prompt
Please design a software architecture for a Geometry Dash clone written in Python. Please write the architecture notes in markdown. When doing this, abide by the following: 1) choose the most explicit approach that is easiest to reason about; 2) follow industry best-practices in software development; 3) error handling and maintainability are paramount. As a note, this package will use tkinter for the GUI.

# Response
Geometry Dash Clone in Python (tkinter) — Architecture Notes

Goal: an explicit, easy-to-reason-about architecture that is maintainable, testable, and robust.
Non-goals: “clever” abstractions, heavy metaprogramming, implicit global state.

⸻

1) High-level shape

Use a layered architecture with a clean dependency direction:
	•	UI Layer (tkinter): renders, handles input events, schedules frame updates.
	•	Application Layer: orchestrates game loop, scenes, resource loading, persistence.
	•	Domain Layer: pure game logic (physics, collisions, rules) with minimal GUI knowledge.
	•	Infrastructure Layer: file I/O, level serialization, audio wrapper, logging, settings.

Dependency direction (top calls down only):

UI → Application → Domain → Infrastructure
Infrastructure may be used by Application (and sometimes Domain via interfaces), but avoid Domain importing tkinter or filesystem code.

⸻

2) Repository layout

```
gdclone/
  pyproject.toml
  README.md
  gdclone/
    __init__.py
    main.py

    app/
      __init__.py
      game_app.py          # bootstrap + dependency wiring
      game_loop.py         # dt, tick scheduling, fixed-step logic
      scene_manager.py     # transitions + scene stack
      scenes/
        __init__.py
        base_scene.py
        menu_scene.py
        play_scene.py
        editor_scene.py

    ui/
      __init__.py
      tk_root.py           # root window creation + scaling policy
      tk_canvas_view.py    # draws domain state onto Canvas
      input_mapper.py      # tkinter events -> input state
      hud_widgets.py       # HUD / overlays
      dialogs.py           # error dialogs, confirmations

    domain/
      __init__.py
      constants.py
      types.py             # dataclasses for state
      world.py             # World update entry point
      physics.py           # integration, gravity, jump model
      collision.py         # AABB / polygon helpers; obstacle tests
      entities/
        __init__.py
        player.py
        obstacle.py
        collectible.py
      level/
        __init__.py
        level_model.py     # in-memory representation
        level_rules.py     # validation and constraints
      systems/
        __init__.py
        progress.py        # percent complete, checkpoints
        scoring.py
        effects.py         # shake, flash logic (domain-side signals)

    infra/
      __init__.py
      logging_setup.py
      clock.py             # monotonic time provider
      resources/
        __init__.py
        asset_loader.py    # images, sounds (with caching)
        paths.py
      persistence/
        __init__.py
        settings_store.py  # json; atomic write
        profile_store.py
      serialization/
        __init__.py
        level_codec.py     # JSON schema encode/decode + versioning

    errors/
      __init__.py
      exceptions.py        # typed exceptions hierarchy
      result.py            # Result[T, E] helper (optional explicit style)

    tests/
      test_physics.py
      test_collision.py
      test_level_codec.py
```

⸻

3) Key principles

Explicit state flow
	•	Maintain a single authoritative GameState (domain dataclasses) that is updated by the domain.
	•	UI is a projection of state: it reads state and draws it.
	•	Avoid “pulling” information from tkinter widgets inside the domain.

Fixed-step simulation
	•	Use a fixed tick for logic (e.g., 1/120s) for determinism and easier testing.
	•	Rendering can be variable (tkinter after), but logic should step in fixed increments.

No hidden globals
	•	No module-level singleton state.
	•	Use dependency injection in game_app.py: pass in Clock, Logger, AssetLoader, etc.

Typed errors + predictable recovery
	•	Use custom exception types for:
	•	AssetLoadError, LevelDecodeError, LevelValidationError, AudioError, PersistenceError.
	•	Catch at scene boundaries and show a user-friendly dialog + safe fallback (e.g., return to Menu).

⸻

4) Game loop design (tkinter-friendly)

tkinter is single-threaded; do not run long tasks on the UI thread.

Loop responsibilities
	•	Collect input state (pressed/released).
	•	Advance simulation by fixed-step ticks (possibly multiple per frame to catch up).
	•	Render current scene to Canvas.
	•	Handle scene transitions and errors.

GameLoop pseudo-contract
	•	start() schedules the first after.
	•	Every frame:
	•	compute frame_dt via Clock.monotonic()
	•	accumulate dt, run while accumulator >= fixed_dt: scene.update(fixed_dt)
	•	scene.render(renderer)
	•	schedule next frame

Spiral-of-death protection
	•	Clamp frame_dt to a max (e.g., 0.1s) so a pause doesn’t cause thousands of ticks.
	•	Cap ticks per frame (e.g., 5–10) and drop remainder with a warning.

⸻

5) Scenes (stateful, explicit boundaries)

Use scenes to isolate complexity and keep error handling localized.

Scene interface

```python
class Scene(Protocol):
    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def handle_input(self, input_state: InputState) -> None: ...
    def update(self, dt: float) -> None: ...
    def render(self, renderer: Renderer) -> None: ...
```

	•	MenuScene: buttons, settings, load level list.
	•	PlayScene: owns World instance and current GameState.
	•	EditorScene: manipulates LevelModel, validates continuously, saves via codec.

Scene transitions are managed via SceneManager:
	•	push(scene), pop(), replace(scene).

⸻

6) Domain model

Prefer simple dataclasses and explicit update functions.

Core types
	•	Vec2: simple immutable vector (or tuple) for position/velocity.
	•	PlayerState: position, velocity, grounded, alive, jump_cooldown, hitbox.
	•	Obstacle: geometry + behavior flags (spikes, blocks, moving platforms).
	•	LevelModel: list of obstacles + metadata + spawn point + length.
	•	GameState: player + camera + progress + flags.

Domain entry point

World.step(state: GameState, level: LevelModel, input: InputState, dt: float) -> GameState
	•	Pure function style is ideal for testing, but if performance becomes an issue, allow controlled mutation inside World while keeping a single entry point.

Collision
	•	Keep collision helpers pure and unit-testable.
	•	Represent hitboxes explicitly (AABB or polygon). Start with AABB for simplicity, only upgrade if needed.

⸻

7) Rendering approach (tkinter Canvas)

Renderer wrapper

Create a small Renderer abstraction that targets Canvas but stays simple:
	•	clear()
	•	draw_rect(x, y, w, h, tag=...)
	•	draw_image(asset_id, x, y, anchor=...)
	•	draw_text(...)
	•	present() (no-op for tkinter, but keeps interface consistent)

Important: avoid creating thousands of new canvas items each frame. Prefer:
	•	Use tags ("player", "obstacles", "hud") and update existing items.
	•	Or clear and redraw only if item count is small—measure early.

Coordinate systems
	•	Domain uses world coordinates (float).
	•	Renderer converts to screen coordinates with:
	•	camera offset
	•	scaling policy (integer scale to preserve crispness)
	•	y-axis direction consistency (tkinter y grows downward—domain can match for simplicity)

⸻

8) Input handling

Use an InputState object updated by tkinter events:
	•	jump_pressed (edge)
	•	jump_held (level)
	•	pause_pressed
	•	restart_pressed

Implementation: InputMapper listens to <KeyPress> / <KeyRelease> and updates a dictionary of key states. Every frame, compute edges (pressed this frame).

This avoids logic reading tkinter events directly.

⸻

9) Level format + validation

Serialization
	•	JSON with an explicit version number, e.g.:

```json
{ "version": 1, "meta": {...}, "obstacles": [...], "length": 123.0 }
```

Versioning policy
	•	LevelCodec.decode():
	•	reads version
	•	dispatches to per-version decoder
	•	migrates older versions into current in-memory model when possible

Validation
	•	LevelRules.validate(level) -> list[LevelValidationIssue]
	•	Do not rely on “it’ll crash later.” Validate on load and before save.

If invalid:
	•	In PlayScene: show error and return to MenuScene.
	•	In EditorScene: show inline warnings but allow fixing.

⸻

10) Resources (assets) and loading strategy

AssetLoader
	•	Central cache keyed by logical IDs ("player_idle", "spike")
	•	Loads images via PIL if available; otherwise tkinter PhotoImage with limitations.
	•	Ensures lifetime: tkinter images must be referenced to avoid garbage collection.

Error handling
	•	Missing asset → AssetLoadError with asset id + path.
	•	Scene catches and shows dialog; fallback to placeholder rectangle if possible.

⸻

11) Persistence (settings, profiles)

Atomic writes

When saving JSON:
	•	write to temp file in same directory
	•	flush, fsync (where possible)
	•	atomic replace (e.g., os.replace)

Settings
	•	SettingsStore.load() returns defaults on first run.
	•	Corrupt file:
	•	back it up (settings.json.corrupt-<timestamp>)
	•	restore defaults
	•	log warning + show one-time notification

⸻

12) Logging + observability

Logging
	•	Configure Python logging once in infra/logging_setup.py
	•	Log to:
	•	rotating file (logs/app.log)
	•	console (dev)
	•	Use structured-ish context in messages (level id, scene, exception type).

Crash boundary

At the top-level (main.py), wrap GameApp.run():
	•	catch Exception
	•	log stack trace
	•	show a friendly fatal dialog with “Open logs” button (optional)
	•	exit cleanly

⸻

13) Concurrency policy (important with tkinter)
	•	UI thread: all tkinter calls.
	•	Background thread: optional for asset preloading or heavy file operations.
	•	Communication: thread-safe queue polled by after() to integrate results into UI.

Avoid touching tkinter objects from background threads.

⸻

14) Testing strategy

Unit tests (fast)
	•	domain/physics.py, domain/collision.py, domain/level_rules.py, infra/serialization/level_codec.py

Deterministic simulation tests
	•	Use fixed dt and recorded inputs to ensure player dies / survives expected sequences.

Integration tests (limited)
	•	Scene transitions without starting tkinter mainloop (test application services and state changes).

⸻

15) Minimal boot flow
	1.	main.py configures logging, builds dependencies, creates GameApp.
	2.	GameApp creates tkinter root + Canvas view + InputMapper.
	3.	SceneManager starts with MenuScene.
	4.	GameLoop.start() begins scheduling ticks via root.after(...).

⸻

16) “Explicit first” coding conventions
	•	@dataclass(frozen=True) for immutable value types (Vec2, config).
	•	@dataclass mutable only for clearly-owned state.
	•	Type hints everywhere; enable mypy (or pyright) in CI.
	•	Keep functions short; prefer single responsibility.
	•	Avoid magic numbers: centralize tuning parameters in domain/constants.py.
	•	Document invariants at the type boundary (e.g., “player x always increases in auto-run mode”).

⸻

If you want, I can also provide a concrete skeleton (empty modules + key class stubs) and a sample GameLoop + PlayScene implementation that adheres to this architecture.

# Prompt
Given this architecture, write me a short prompt that explains the software architecture so I can use it for future queries.

# Response
Here’s a concise, reusable prompt you can paste at the start of future conversations to re-establish the context:

⸻

Context: Geometry Dash Clone Architecture (Python + tkinter)

We are working on a Geometry Dash–style game written in Python using tkinter. The project follows an explicit, layered architecture prioritizing maintainability, error handling, and ease of reasoning.

Architecture overview:
	•	UI Layer (ui/): tkinter-only code (Canvas rendering, input mapping, dialogs). No game logic.
	•	Application Layer (app/): game loop (fixed-step), scene management, orchestration, dependency wiring.
	•	Domain Layer (domain/): pure game logic (physics, collisions, entities, world updates, level rules). No tkinter or filesystem imports.
	•	Infrastructure Layer (infra/): assets, serialization, persistence, logging, clocks.

Key patterns & rules:
	•	Single authoritative GameState updated via World.step(...).
	•	Fixed-step simulation (e.g., 120 Hz), variable-rate rendering via tk.after.
	•	Scene-based flow (MenuScene, PlayScene, EditorScene) managed by a SceneManager.
	•	No global state; dependencies are injected explicitly.
	•	Typed custom exceptions (AssetLoadError, LevelDecodeError, etc.) caught at scene boundaries.
	•	JSON-based level format with versioning and validation.
	•	Renderer abstraction over tkinter.Canvas.
	•	All tkinter calls stay on the UI thread.

Assume this architecture unless explicitly stated otherwise, and prefer explicit, testable, industry-standard solutions over clever or implicit ones.

⸻

# Notes
