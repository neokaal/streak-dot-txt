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

Create a virtual environment, then use the Make targets for routine work:

```bash
python3 -m venv .env
make install
make check
```

On Windows, use `.env\Scripts\python` in place of `.env/bin/python`.
If `make` is unavailable, each target expands to the Python, Cargo, or npm
command documented below it in `Makefile`.

The dependency sets are:

- `requirements.txt`: application runtime
- `requirements-dev.txt`: runtime plus automated testing
- `requirements-build.txt`: runtime plus PyInstaller
- `requirements.lock`: exact Python 3.13 constraints used for release work

## Run locally

CLI:

```bash
make run-cli
```

Local web application and API:

```bash
make run-api
```

Then open `http://127.0.0.1:8000`. API documentation is available at
`http://127.0.0.1:8000/docs`.

Legacy Tkinter interface:

```bash
.env/bin/python streaksgui.py
```

Tauri desktop development window:

```bash
make run-desktop
```

The desktop command starts and stops the local API with the Tauri process.
It requires Node.js, Rust, and the dependencies in `desktop/package-lock.json`.
The Unix convenience wrapper `desktop/run-local.sh` runs the same Python
launcher.

## Test

```bash
make test
make check
make coverage
```

`make check` runs Python and Rust tests, Python compilation, dependency checks,
Rust formatting validation, and a release-mode Rust check. To build and measure
the packaged sidecar against temporary streak data, run
`make benchmark-startup`.

Tests that use streak files receive a unique temporary directory. No automated
test should use the normal `~/streaks` directory.

## Build a desktop release

Install the pinned build dependencies first:

```bash
make install
```

Build the native bundles for the current operating system:

```bash
make distribute
```

Run that command from the repository root. Windows uses the same Python script
with `.env\Scripts\python`. Build each operating-system target on that operating
system.

On macOS, build only the `.app` without invoking Finder-based DMG layout
automation:

```bash
make release-app
```

The default build asks Tauri for all configured bundles, including DMG on
macOS. Resulting installers are placed under
`desktop/src-tauri/target/release/bundle/`.

The packaged sidecar chooses a free loopback port, verifies a per-launch
identity token, and is terminated when Tauri exits. If startup fails, the
desktop window displays the path to `sidecar.log`.

Useful release targets:

- `make build`: compile Python and the release-mode Rust shell without bundling.
- `make build-sidecar`: build only the embedded Python server.
- `make release-app`: verify and build the macOS `.app` without Finder automation.
- `make distribute`: verify and build every configured installer for the current OS.
- `make clean`: remove only known generated build and coverage directories.

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
