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


def build_release(bundles: str | None = None) -> None:
    sidecar = build_sidecar()
    destination = DESKTOP_DIR / "src-tauri" / "resources" / "sidecar"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(sidecar.parent, destination)

    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("npm is required to build the Tauri bundle")
    command = [npm, "run", "build"]
    if bundles:
        command.extend(["--", "--bundles", bundles])
    subprocess.run(command, check=True, cwd=DESKTOP_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundles",
        help="Tauri bundle list, for example app or app,dmg",
    )
    arguments = parser.parse_args()
    build_release(arguments.bundles)


if __name__ == "__main__":
    main()
