"""Build the native Streak.txt bundle for the current operating system."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

try:
    from .package_sidecar import DESKTOP_DIR, build_sidecar
except ImportError:
    from package_sidecar import DESKTOP_DIR, build_sidecar


def rust_target_triple() -> str:
    result = subprocess.run(
        ["rustc", "-vV"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("host: "):
            return line.removeprefix("host: ")
    raise RuntimeError("rustc did not report a host target")


def build_release(target_triple: str | None = None, bundles: str | None = None) -> None:
    sidecar = build_sidecar()
    target_triple = target_triple or rust_target_triple()
    suffix = sidecar.suffix if sidecar.suffix == ".exe" else ""
    destination = (
        DESKTOP_DIR
        / "src-tauri"
        / "binaries"
        / f"streak-server-{target_triple}{suffix}"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sidecar, destination)

    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("npm is required to build the Tauri bundle")
    command = [npm, "run", "build"]
    if bundles:
        command.extend(["--", "--bundles", bundles])
    subprocess.run(command, check=True, cwd=DESKTOP_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="override the rustc host target")
    parser.add_argument(
        "--bundles",
        help="Tauri bundle list, for example app or app,dmg",
    )
    arguments = parser.parse_args()
    build_release(arguments.target, arguments.bundles)


if __name__ == "__main__":
    main()
