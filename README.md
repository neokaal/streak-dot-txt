# Streak.txt

Streak.txt is a local-first tracker for repeated practices and routines. Every
streak remains a readable text file on your disk; completing a period appends a
date, while missing a period requires no entry.

```text
---
name: Jumping Jacks
tick: Daily
---
2025-01-01
2025-01-03
2025-01-04
```

Normal CLI, web, Tkinter, and packaged-desktop launches use `~/streaks`.
`STREAKS_DIR` and the CLI `--dir` option are deliberate overrides for
development or alternate collections. Automated tests always use isolated
temporary directories and do not touch `~/streaks`.

## Install for development

Create a virtual environment and install the locked development dependencies:

```bash
python3 -m venv .env
.env/bin/python -m pip install -c requirements.lock -r requirements-dev.txt
```

On Windows, use `.env\Scripts\python` in place of `.env/bin/python`.

The dependency sets are:

- `requirements.txt`: application runtime
- `requirements-dev.txt`: runtime plus automated testing
- `requirements-build.txt`: runtime plus PyInstaller
- `requirements.lock`: exact Python 3.13 constraints used for release work

## Run locally

CLI:

```bash
.env/bin/python streakdottxt.py --help
.env/bin/python streakdottxt.py list
```

Local web application and API:

```bash
.env/bin/python run_api.py
```

Then open `http://127.0.0.1:8000`. API documentation is available at
`http://127.0.0.1:8000/docs`.

Legacy Tkinter interface:

```bash
.env/bin/python streaksgui.py
```

Tauri desktop development window:

```bash
.env/bin/python desktop/run_local.py
```

The desktop command starts and stops the local API with the Tauri process.
It requires Node.js, Rust, and the dependencies in `desktop/package-lock.json`.
The Unix convenience wrapper `desktop/run-local.sh` runs the same Python
launcher.

## Test

```bash
.env/bin/python -m pytest -q
cd desktop/src-tauri && cargo test
```

For a coverage report, put the virtual environment first on `PATH` and run
`./run_tests.sh`.

Tests that use streak files receive a unique temporary directory. No automated
test should use the normal `~/streaks` directory.

## Build a desktop release

Install the pinned build dependencies first:

```bash
.env/bin/python -m pip install -c requirements.lock -r requirements-build.txt
cd desktop
npm ci
```

Build the native bundles for the current operating system:

```bash
.env/bin/python desktop/package_release.py
```

Run that command from the repository root. Windows uses the same Python script
with `.env\Scripts\python`. Build each operating-system target on that operating
system.

On macOS, build only the `.app` without invoking Finder-based DMG layout
automation:

```bash
.env/bin/python desktop/package_release.py --bundles app
```

The default build asks Tauri for all configured bundles, including DMG on
macOS. Resulting installers are placed under
`desktop/src-tauri/target/release/bundle/`.

The packaged sidecar chooses a free loopback port, verifies a per-launch
identity token, and is terminated when Tauri exits. If startup fails, the
desktop window displays the path to `sidecar.log`.

## Release version

The current release is `0.1.0`, codename **Hearth Pheasant**. Update all
checked-in Python, Cargo, npm, and Tauri version markers with:

```bash
.env/bin/python scripts/set_version.py 0.2.0
```

Review the resulting diff and run the complete automated suite before
committing a version change.

Generated Tauri configuration schemas under `desktop/src-tauri/gen/schemas/`
are intentionally versioned for editor and configuration validation. Build
trees, bundled sidecars, installers, `node_modules`, and platform binaries are
generated artifacts and remain ignored.

## File storage

New files use the canonical convention `streak-{id}.txt`, where the ID is a
lowercase slug derived from the display name. For example, `Read / Reflect`
becomes `streak-read-reflect.txt`. Existing legacy filenames remain readable.
Archived streaks move into `~/streaks/archive/` without overwriting older
archives.

The format documentation and project site live in
[`docs/`](https://abhishekmishra.github.io/streak-dot-txt/).
