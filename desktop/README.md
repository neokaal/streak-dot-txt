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

Run `./package-release.sh` on the operating system you are packaging for. It
builds the Python sidecar, gives it Tauri's required platform-specific name,
and creates the native installer. The installer is written under
`src-tauri/target/release/bundle/`.

Build each target on its own operating system. The upcoming CI release workflow
will build one artifact for macOS, Windows, and Linux; signing and notarization
are separate release credentials, not part of ordinary local builds.
