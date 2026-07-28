# Streak.txt desktop shell

This is a thin Tauri wrapper around the bundled local FastAPI application.
The repository [`README.md`](../README.md) is the authoritative guide for
installation, development, testing, packaging, and version updates.

Cross-platform Python entry points:

```bash
# Development window
.env/bin/python desktop/run_local.py

# Native bundles for the current OS
.env/bin/python desktop/package_release.py

# macOS .app only, without Finder-based DMG layout automation
.env/bin/python desktop/package_release.py --bundles app
```

The shell wrappers in this directory are Unix conveniences around those Python
entry points.

Release builds use `~/streaks`, choose a free loopback port, verify that they
connected to the sidecar from the current launch, and terminate that process on
exit. Startup failures are shown in the window with the platform-specific
location of `sidecar.log`.

PyInstaller produces a directory-based sidecar that Tauri bundles as an
application resource. Keeping the interpreter support files beside the
executable avoids the extraction delay of a one-file sidecar.
