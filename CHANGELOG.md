# CHANGELOG

This file documents major changes in every release of the project.
The project follows [Semantic Versioning](https://semver.org/). There is a
section for each release, which lists major changes made in the release.

**0.1.1**  2026-07-30 Abhishek Mishra

- Moved the project to the NeokaaL GitHub organization and relocated its
  public site to `neokaal.com/open/streakdottxt/`.
- Reduced release-workflow permissions, isolated release publishing from
  native builds, and limited repository automation to SHA-pinned,
  GitHub-authored actions.
- Replaced the external Rust setup action with a repository-owned, pinned Rust
  toolchain definition and added reviewed dependency-update automation.

**0.1.0**  2026-07-28 Abhishek Mishra

- Added the first Streak.txt desktop release for macOS Apple Silicon and
  64-bit Windows, with an offline local service bundled into each installer.
- Reworked the daily screen as a compact, fixed-position switchboard using the
  four-color Dusty4 palette, stable streak ordering, and clear completed states.
- Kept streak data local and portable as human-readable text files, with
  collection settings stored alongside the streaks.
- Unified the desktop, web, CLI, and Tkinter interfaces around shared parsing,
  validation, statistics, and safe file-handling behavior.
- Hardened the local application with loopback-only networking, write-origin
  protection, dynamic ports, verified sidecar startup, and useful failure logs.
- Added reproducible native packaging, automated checks, and a draft-release
  workflow for unsigned macOS and Windows builds.
