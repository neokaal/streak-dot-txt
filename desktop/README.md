# Streak.txt desktop shell

This is a deliberately thin Tauri wrapper. The product interface is served by
the bundled local FastAPI server; Tauri provides the native application window
and release packaging only.

## Development

Run `./run-local.sh` from this directory. It starts the local server, opens the
Tauri development window, and stops the server when the window exits. By
default it uses `~/streaks`.

Set `STREAKS_DIR=/path/to/streaks` before the command only when deliberately
using a different collection. Release builds start their bundled sidecar without
an override, so they also use `~/streaks`.

## Release packaging

`./package-sidecar.sh` creates a platform-specific `streak-server` executable
with PyInstaller. Rename it using Tauri's target-triple convention and place it
in `src-tauri/binaries/` before `npm run tauri build`. CI will eventually build
one release per target and provide code signing/notarization credentials.
