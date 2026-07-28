# Backlog

This backlog tracks upcoming work in release-sized groups, with the newest
planned release at the top and older releases below it. Keep completed items
checked here until they are moved into release notes or archived.

## v0.1.0 - Hearth Pheasant

### Data Integrity and File Handling

- [x] Use one canonical streak ID and filename derivation path across the repository and file manager.
- [x] Reject invalid streak names and tick types before creating or modifying any files.
- [x] Detect unexpected end-of-file while parsing metadata and ticks instead of hanging indefinitely.
- [x] Isolate malformed or unreadable streak files so one bad file cannot take down the complete dashboard.
- [x] Preserve every archived streak by preventing silent overwrites when an archive filename already exists.
- [x] Define and enforce safe escaping or validation for metadata values written to streak files.
- [x] Reconcile the advertised Monthly tick type with the tick types actually supported by the model and parser.

### Desktop Runtime

- [x] Retain and manage the sidecar process handle so the server shuts down when the desktop application exits.
- [x] Replace the fixed desktop server port with a dynamically selected port.
- [x] Verify the identity and readiness of the Streak.txt sidecar before redirecting the desktop shell.
- [x] Add a bounded startup timeout and surface useful sidecar startup errors in the desktop window.
- [ ] Reduce first-launch latency caused by the one-file sidecar bundle.

### Local Application Security

- [x] Bind the standalone local API to `127.0.0.1` by default instead of exposing it to the local network.
- [x] Protect local write endpoints from cross-origin create and tick requests.
- [x] Encode streak IDs safely when inserting them into URLs, HTML IDs, and CSS selectors.

### Web Application

- [x] Bundle HTMX with the application so the desktop UI remains fully functional offline.

### Streak and Statistics Correctness

- [x] Include the ISO year when detecting duplicate weekly ticks.
- [x] Normalize weekly tick dates consistently before calculating current and longest streaks.
- [x] Define statistics behavior for duplicate, unsorted, and future-dated ticks and cover it with tests.
- [x] Keep model invariants synchronized when metadata changes the tick type or period.

### Unified Architecture

- [ ] Migrate the CLI to the unified repository and service layer.
- [ ] Migrate the Tkinter application to the unified repository and service layer while it remains supported.
- [ ] Remove or migrate the unused legacy API endpoints that bypass current validation, archive, and response behavior.

### Automated Testing

- [x] Replace the unittest-only test command with a runner that executes the complete pytest suite.
- [x] Give every filesystem test its own temporary directory instead of sharing and clearing `/tmp/test_streaks`.
- [x] Add regression tests for malformed files, filename normalization, invalid tick types, archive collisions, and weekly year boundaries.
- [ ] Add automated tests for desktop sidecar lifecycle and readiness logic without launching the desktop UI.

### Packaging and Releases

- [ ] Provide packaging entry points that work on macOS, Linux, and Windows without assuming Unix shell paths and tools.
- [ ] Separate runtime, test, and packaging dependencies and lock versions for reproducible builds.
- [ ] Establish a release-version update process covering the Python package, Cargo package, Tauri configuration, and generated artifacts.
- [x] Make packaged sidecar logs and failures available for troubleshooting installed builds.
- [ ] Provide a macOS packaging path that does not require Finder automation for routine builds.

### Repository and Documentation

- [ ] Document the supported local, desktop development, and distribution workflows in one authoritative location.
- [ ] Update stale API documentation to match the current `streak-{id}.txt` storage convention.
- [ ] Decide which generated Tauri files and release artifacts belong in version control and ignore the remainder.
