# Desktop release process

Streak.txt desktop releases currently contain two native installers:

- an identity-free ad-hoc-signed and unnotarized macOS DMG for Apple Silicon
  and macOS 11 or newer
- an unsigned Windows NSIS installer for 64-bit Windows

The macOS application requires a manual Gatekeeper override, and the Windows
installer may trigger a Microsoft Defender SmartScreen warning. Changing these
policies requires separate project-ownership decisions and platform signing
credentials.

## Signing policy

The initial open-source release does not use a corporate Apple Developer
identity or a Windows code-signing certificate. Tauri seals the macOS bundle
with the ad-hoc pseudo-identity `-`, which uses no Apple account but prevents
macOS from treating the downloaded bundle as structurally broken. The release
workflow therefore requires no long-lived signing credentials. It uses
GitHub's short-lived repository token only to create and update a draft
release.

If repository ownership changes later, signing can be added without changing
the release artifact types or the tag-to-draft workflow.

## Prepare a release

1. Confirm the intended release backlog is complete.
2. Update all version markers:

   ```bash
   .env/bin/python scripts/set_version.py 0.2.0
   ```

3. Add the release at the top of `CHANGELOG.md` with its version, release date,
   maintainer, and concise user-facing changes.
4. Update other user-facing documentation when behavior or support changes.
5. Run `make check` from a clean working tree.
6. Commit the release preparation and review the resulting commit.

Do not create or push a release tag until the release preparation has been
reviewed.

## Build the draft release

1. Push the reviewed release preparation to `main`.
2. Run the `Desktop release` workflow manually and download its private,
   short-lived artifacts to confirm both native builds complete.
3. Create the matching annotated tag, such as `v0.2.0`, and push that tag.
4. The tag-triggered workflow verifies that the tag matches
   the application version.
5. The workflow builds both native installers, creates a draft GitHub Release,
   and uploads `SHA256SUMS.txt`.

The draft remains private until a maintainer publishes it.

## Verify and publish

Download the artifacts from the draft release and test them on clean systems.

On macOS:

- open the DMG and install the application
- attempt to launch it, then use **System Settings → Privacy & Security → Open
  Anyway** and confirm the application opens
- create and tick a streak, restart, and confirm persistence
- uninstall the application and confirm the streak files remain

On Windows:

- install through the expected SmartScreen warning
- launch the application and confirm the bundled service starts
- create and tick a streak, restart, and confirm persistence
- uninstall the application and confirm the streak files remain

Confirm the checksum file covers both installers. Review the changelog-derived
release notes and download links, then publish the draft release manually.
Finally, open the next release section in `BACKLOG.md` and copy its repeatable
release checklist.
