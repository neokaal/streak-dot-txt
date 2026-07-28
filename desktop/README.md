# Streak.txt desktop shell

This is a thin Tauri wrapper around the bundled local FastAPI application.
The repository [`README.md`](../README.md) is the authoritative guide for
installation, development, testing, packaging, and version updates.

Routine targets from the repository root:

```bash
# Development window
make run-desktop

# Native bundles for the current OS
make distribute

# macOS .app only, without Finder-based DMG layout automation
make release-app

# Isolated sidecar startup measurement
make benchmark-startup
```

The Make targets call cross-platform Python entry points in this directory.
Those scripts can also be invoked directly on systems without `make`.

Release builds use `~/streaks`, choose a free loopback port, verify that they
connected to the sidecar from the current launch, and terminate that process on
exit. Startup failures are shown in the window with the platform-specific
location of `sidecar.log`.

PyInstaller produces a directory-based sidecar that Tauri bundles as an
application resource. Keeping the interpreter support files beside the
executable avoids the extraction delay of a one-file sidecar.
