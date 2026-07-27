# Streak.txt desktop shell

This is a deliberately thin Tauri wrapper. The product interface is served by
the bundled local FastAPI server; Tauri provides the native application window
and release packaging only.

## Development

1. In one terminal, run `STREAKS_DIR=/path/to/streaks .env/bin/python -m uvicorn streak_api.main:app --host 127.0.0.1 --port 8000`.
2. Run `npm install` and `npm run tauri dev` from this directory.

Tauri opens `http://127.0.0.1:8000`. Development intentionally keeps the server
separate so UI work remains quick and Python debugging stays straightforward.
Release builds start their bundled sidecar and configure it with `~/streaks`.

## Release packaging

`./package-sidecar.sh` creates a platform-specific `streak-server` executable
with PyInstaller. Rename it using Tauri's target-triple convention and place it
in `src-tauri/binaries/` before `npm run tauri build`. CI will eventually build
one release per target and provide code signing/notarization credentials.
