# Streak.txt

Streak.txt is a local-first desktop tracker for repeated practices and routines.
It presents your streaks as a compact, fixed-position switchboard while keeping
the underlying data in readable text files on your disk.

[Download the latest release](https://github.com/abhishekmishra/streak-dot-txt/releases/latest)
· [Project site and format guide](https://abhishekmishra.github.io/streak-dot-txt/)

## The format

Each streak is one file. Completing a period appends its date; missing a period
requires no entry.

```text
---
name: Morning Walk
tick: Daily
---
2026-07-25
2026-07-26
2026-07-28
```

Files normally live in `~/streaks` and use the
`streak-<id>.txt` naming convention. Collection settings, including stable
panel order, live beside them in `streaks-config.json`. Existing legacy
filenames remain readable.

## Desktop releases

The current release supports:

- macOS 11 or newer on Apple Silicon
- 64-bit Windows

The initial builds are not signed with commercial platform credentials. macOS
requires a one-time Gatekeeper override, and Windows may display a Microsoft
Defender SmartScreen warning. Checksums accompany every release.

The application works offline, binds its bundled service only to `127.0.0.1`,
and does not remove streak files when uninstalled.

## Command line

The Python CLI reads and writes the same files as the desktop application.

```bash
python3 -m venv .env
make install

.env/bin/python streakdottxt.py list
.env/bin/python streakdottxt.py new --name "Morning Walk"
.env/bin/python streakdottxt.py tick --name "morning"
.env/bin/python streakdottxt.py view --name "morning"
```

On Windows, use `.env\Scripts\python` in place of `.env/bin/python`. Pass
`--dir` to use a collection outside `~/streaks`.

## Development

The shared Python core handles parsing, validation, statistics, and file
operations. FastAPI and HTMX provide the local interface, and Tauri packages it
as a native desktop application.

```bash
make install       # install development dependencies
make run-api       # local web interface on 127.0.0.1:8000
make run-desktop   # Tauri development window
make test          # Python and Rust tests
make check         # complete pre-commit verification
make distribute    # native installer for the current platform
```

Tests always use isolated temporary directories and must never touch
`~/streaks`. See [AGENTS.md](AGENTS.md) for the architecture and safety rules.

Packaging and publication are documented in
[docs/release-process.md](docs/release-process.md). Release history is recorded
in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE) © Abhishek Mishra
