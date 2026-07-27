# Desktop and web architecture

## Status

Proposed design. This document is the implementation outline for replacing the
Tkinter application with a local-first web application and cross-platform
desktop app.

## Goals

- Keep streak data as human-editable `streak-*.txt` files.
- Provide one authoritative set of streak operations for every interface.
- Ship a responsive browser experience and a native-feeling desktop experience
  for macOS, Windows, and Linux.
- Work entirely offline and without an account in the first release.
- Preserve the CLI while removing presentation-specific business logic.

## Non-goals for the first release

- Cloud sync, accounts, multi-user access, or a hosted service.
- Mobile applications.
- Replacing the plain-text storage format with a database.
- A JavaScript single-page application.

## Proposed architecture

```text
                         +---------------------------+
                         | Tauri desktop shell        |
                         | native window + OS actions |
                         +-------------+-------------+
                                       |
Browser -------------------------------+-- HTTP on localhost
                                       v
                         +---------------------------+
                         | FastAPI application       |
                         | REST API + HTML routes     |
                         | Jinja templates + HTMX    |
                         +-------------+-------------+
                                       |
                         +---------------------------+
                         | StreakService              |
                         | validation + use cases     |
                         +-------------+-------------+
                                       |
              +------------------------+------------------------+
              |                                                 |
   +----------v-----------+                         +-----------v----------+
   | streak_core          |                         | StreakRepository     |
   | models + statistics  |                         | plain-text file I/O  |
   +----------------------+                         +----------------------+
```

The FastAPI application remains the local server. It exposes JSON endpoints
for integrations and renders HTML for the browser and desktop UI. Tauri starts
the bundled server, opens a native window to its localhost address, and owns
desktop-only capabilities such as notifications and opening folders.

## Responsibilities

### `streak_core`

- Domain models, tick/date rules, parsing and formatting primitives, and
  statistics calculations.
- No FastAPI, CLI, Tkinter, filesystem-path selection, or HTML concerns.

### `StreakRepository`

- Locate, load, create, save, archive, and list streak files in one configured
  directory.
- Use stable streak IDs derived from a validated slug, not display names or
  arbitrary paths.
- Use atomic writes and preserve a predictable file format.

### `StreakService`

- The unified application API used by routes and the CLI.
- Load and calculate stats consistently; validate tick types and duplicate
  ticks; sort normalized entries.
- Return domain results and application errors, not HTTP responses.

### FastAPI application

- JSON API under `/api/v1` for programmatic use.
- Browser routes under `/` and HTMX partial routes under `/ui` (exact paths to
  be finalized during implementation).
- Translate service errors into HTTP responses; own request/form validation.
- Bind only to `127.0.0.1` by default. Do not retain permissive CORS in the
  local desktop configuration.

### Tauri shell

- Package and launch the FastAPI server as a per-platform sidecar.
- Wait for a local health check, pass the selected data directory safely, and
  shut the sidecar down when the application exits.
- Provide a single app window initially; add tray, notifications, and startup
  behavior only after the core desktop flow works.
- Keep Rust code limited to shell lifecycle and explicitly approved OS access.

## First user experience

1. Open the desktop app or visit the local browser URL.
2. See today's date and a dashboard of all streaks.
3. Tick or undo a streak from its card; HTMX replaces only the affected card
   and summary.
4. Create a streak from an inline/modal form.
5. Open a streak detail page with its history, stats, and edit controls.
6. Choose or open the streak directory through a desktop action or a settings
   page.

## Data and safety rules

- Streak ID is the validated slug used in `streak-<id>.txt`; names are display
  metadata and may not be used as file paths.
- One tick per relevant period is allowed. Duplicate attempts are idempotent
  for the quick-tick action and reported clearly for explicit historical edits.
- Writes are atomic to avoid corrupting a file after an interrupted save.
- Deletion is an archive/move operation, not an irreversible `os.remove`.
- The application is local and single-user initially; any future remote mode
  requires authentication, CSRF protection, and a revised CORS policy.

## Delivery phases

### Phase 1 — stabilize the core

- Introduce repository and service layers.
- Move all loading, save, validation, and stat calculation into those layers.
- Add unit tests for daily/weekly rules, IDs, duplicate ticks, statistics, and
  atomic persistence.
- Keep the CLI working through the service layer.

### Phase 2 — local web UI

- Add Jinja templates, shared styling, and HTMX interactions to FastAPI.
- Build dashboard, quick tick, streak create, detail, edit, and settings
  flows.
- Add route/integration tests covering HTML fragments as well as JSON API
  behavior.
- Make the former Tkinter workflow fully redundant, then remove Tkinter from
  supported entry points.

### Phase 3 — desktop packaging

- Add a Tauri shell that launches the packaged local server.
- Produce development builds for macOS, Windows, and Linux.
- Test first-run directory setup, sidecar lifecycle, offline behavior, and
  upgrades without modifying user streak files.
- Establish release signing/notarization requirements before public releases.

## Open decisions

- Whether the default streak directory remains `~/streaks` or moves to an
  application-data location while retaining the ability to choose any folder.
- Whether undo means removing today's entry immediately or is available only
  from a detail/history view.
- Which desktop features are in the first packaged release: tray menu,
  notifications, launch at login, and file/folder actions.
- Support and release order for macOS, Windows, and Linux.

## Success criteria

- A user can complete all current quick-tick actions without Tkinter.
- CLI, REST API, browser UI, and desktop app produce identical file results.
- The desktop app runs with no separately installed Python or local server.
- Existing valid streak files remain readable and editable by hand.
