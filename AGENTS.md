# Streak.txt agent guide

## Product intent

Streak.txt is a local-first tracker. Streaks are human-readable
`streak-{id}.txt` files, normally in `~/streaks`; the CLI, API, legacy Tkinter
UI, and Tauri desktop app must produce the same results.

Keep the product small and dependable. Treat every new feature as a possible
cost to speed, clarity, and spatial familiarity.

## Architecture

- `streak_core/`: models, parsing, statistics, repository, and shared use cases.
  Keep framework and presentation concerns out of this package.
- `streak_api/`: FastAPI routes plus server-rendered Jinja/HTMX UI.
- `desktop/`: thin Tauri shell and Python packaging/lifecycle tools.
- `streakdottxt.py`: CLI using the shared service layer.
- `tests/` and `test_streakdottxt.py`: automated coverage.

Read `docs/design/desktop-web-architecture.md` before changing boundaries and
`docs/design/ui-direction.md` before changing the daily interface.

## Data and safety

- Never run tests against `~/streaks`. Use `tmp_path`, another temporary
  directory, or an explicit `STREAKS_DIR`.
- Preserve the plain-text streak format and legacy readable filenames.
- Validate IDs before constructing paths; keep writes atomic.
- Archive streaks without overwriting earlier archives; do not hard-delete.
- `streaks-config.json` belongs to the collection and stores portable settings
  such as panel order. Preserve unknown keys when updating it.
- Keep local services bound to `127.0.0.1` and retain write-origin protection.

## UI constraints

- The primary UI is a dense desktop switchboard, not a general dashboard.
- Keep controls in fixed positions after ticking or reloading.
- Preserve the 5 × 5, no-scroll layout at the default 960 × 720 viewport;
  additional rows scroll inside the switchboard without resizing earlier rows.
- Use only the four Dusty4 colors defined in `streak_api/static/app.css`.
- Completion must be obvious without color and must not change geometry.
- Prefer compact controls and one familiar daily view over added navigation,
  modes, or decorative spacing.

## Workflow

Use the repository Make targets:

```bash
make test-python   # focused Python suite
make test          # Python and Rust tests
make check         # complete pre-commit verification
make run-api       # local API/UI on 127.0.0.1:8000
make run-desktop   # API plus Tauri development window
```

The desktop development URL uses port 8000; packaged builds select a free
loopback port. If development reports that 8000 is occupied, identify the
listener instead of terminating an unknown process.

Add regression tests for behavior changes. For UI work, verify the populated
app at 960 × 720 as well as checking rendered HTML. Update `BACKLOG.md` only
when scope is agreed, and mark work complete only after verification.

Do not edit generated build artifacts, packaged binaries, `node_modules`, or
the bundled `streak_api/static/htmx.min.js`.
