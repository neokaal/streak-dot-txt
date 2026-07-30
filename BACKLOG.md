# Backlog

This backlog tracks upcoming work in release-sized groups, with the newest
planned release at the top and older releases below it. Keep completed items
checked here until they are moved into release notes or archived.

## v0.1.1

### Repository Transfer

- [x] Update the local Git remote from the personal repository to `neokaal/streak-dot-txt`.
- [x] Update repository, release-download, and GitHub Pages links to their new NeokaaL locations.
- [x] Restrict GitHub Actions write access to release-publishing jobs and pin every action to an immutable commit.
- [x] Configure Dependabot to propose reviewed updates for pinned GitHub Actions.
- [x] Restrict repository Actions policy to SHA-pinned GitHub-authored actions only.
- [x] Replace the external Rust setup action with a repository-owned, pinned Rust toolchain definition.

## Unplanned

### Automated Testing

- [ ] Run the complete check suite automatically on pushes to `main` and on pull requests.

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
- [x] Reduce packaged sidecar size and warm-start latency; accept the remaining one-time macOS cold-validation delay for unsigned local builds.

### Local Application Security

- [x] Bind the standalone local API to `127.0.0.1` by default instead of exposing it to the local network.
- [x] Protect local write endpoints from cross-origin create and tick requests.
- [x] Encode streak IDs safely when inserting them into URLs, HTML IDs, and CSS selectors.

### Web Application

- [x] Bundle HTMX with the application so the desktop UI remains fully functional offline.

### Daily Switchboard UI

- [x] Replace the responsive card dashboard with a dense, fixed-position desktop grid that keeps 25 streaks visible in the default 960 × 720 window without page scrolling.
- [x] Persist a deterministic panel order so ticking or reloading never moves a streak, and newly created streaks take the next available position without rearranging existing ones.
- [x] Redesign each streak as a compact control with its full name, current/best/rate readouts, and a consistently positioned tick button.
- [x] Give ticked streaks an unmistakable pressed state that remains clear without color and does not change the control's size or position.
- [x] Apply the Dusty4 palette through shared style variables across every normal, hover, focus, and completed state without introducing additional interface colors.
- [x] Keep streak creation available from the daily screen without expanding the page or shifting the switchboard controls.
- [x] Add rendering and interaction regressions for stable ordering and completion states, and verify the populated switchboard at the default desktop viewport.

### Streak and Statistics Correctness

- [x] Include the ISO year when detecting duplicate weekly ticks.
- [x] Normalize weekly tick dates consistently before calculating current and longest streaks.
- [x] Define statistics behavior for duplicate, unsorted, and future-dated ticks and cover it with tests.
- [x] Keep model invariants synchronized when metadata changes the tick type or period.

### Unified Architecture

- [x] Migrate the CLI to the unified repository and service layer.
- [x] Migrate the Tkinter application to the unified repository and service layer while it remains supported.
- [x] Remove or migrate the unused legacy API endpoints that bypass current validation, archive, and response behavior.

### Automated Testing

- [x] Replace the unittest-only test command with a runner that executes the complete pytest suite.
- [x] Give every filesystem test its own temporary directory instead of sharing and clearing `/tmp/test_streaks`.
- [x] Add regression tests for malformed files, filename normalization, invalid tick types, archive collisions, and weekly year boundaries.
- [x] Add automated tests for desktop sidecar lifecycle and readiness logic without launching the desktop UI.

### Packaging and Releases

- [x] Provide Makefile targets for installation, running, testing, checking, building, releasing, distributing, benchmarking, and cleanup.
- [x] Provide packaging entry points that work on macOS, Linux, and Windows without assuming Unix shell paths and tools.
- [x] Separate runtime, test, and packaging dependencies and lock versions for reproducible builds.
- [x] Establish a release-version update process covering the Python package, Cargo package, Tauri configuration, and generated artifacts.
- [x] Make packaged sidecar logs and failures available for troubleshooting installed builds.
- [x] Provide a macOS packaging path that does not require Finder automation for routine builds.

### Repository and Documentation

- [x] Document the supported local, desktop development, and distribution workflows in one authoritative location.
- [x] Update stale API documentation to match the current `streak-{id}.txt` storage convention.
- [x] Decide which generated Tauri files and release artifacts belong in version control and ignore the remainder.

### Release Enablement - One-Time

- [x] Generate and configure production application icons for macOS and Windows.
- [x] Finalize bundle metadata, including the application identifier, displayed version, and minimum supported macOS version.
- [x] Restrict initial release artifacts to a macOS Apple Silicon DMG and a Windows x64 NSIS installer.
- [x] Add a GitHub Actions workflow that runs checks, builds each platform's native Python sidecar, and creates a draft GitHub Release from a version tag.
- [x] Generate and attach SHA-256 checksums for every release artifact.
- [x] Keep the initial open-source release independent of corporate Apple signing credentials.
- [x] Verify the unsigned macOS DMG installs through the documented Gatekeeper override.
- [x] Document supported platforms, installation, the streak data location, and the expected macOS Gatekeeper and Windows SmartScreen warnings.
- [x] Document the tag-to-draft-to-publish release workflow for maintainers.
- [x] Create `CHANGELOG.md` in the established Semantic Versioning format and add the initial `0.1.0` release entry.

### Release Checklist - Copy Into Every Release

- [x] Confirm the release scope is complete and all intended backlog items are checked.
- [x] Update the version everywhere using the repository's version-update process.
- [x] Add the completed release at the top of `CHANGELOG.md` with its version, release date, maintainer, and concise user-facing changes.
- [x] Update user-facing documentation and use the changelog entry as the concise GitHub release notes.
- [x] Run the complete automated check suite from a clean working tree.
- [x] Push the release commit and create the matching version tag.
- [x] Confirm GitHub Actions produces the macOS Apple Silicon DMG, Windows x64 installer, and checksum file in a draft release.
- [x] Install the macOS build on a clean machine and verify the expected signing and notarization policy, launch, ticking, persistence, restart, and uninstall behavior.
- [x] Install the Windows build on a clean machine or virtual machine and verify installation, launch, ticking, persistence, restart, and uninstall behavior.
- [x] Confirm uninstalling either application does not remove the user's streak files.
- [x] Review the draft release notes and download links.
- [x] Publish the release.
- [ ] Open the next release section and copy this release checklist into it.
