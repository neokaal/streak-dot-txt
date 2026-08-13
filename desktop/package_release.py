"""Build the native Streak.txt bundle for the current operating system."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

DESKTOP_DIR = Path(__file__).resolve().parent


def build_release(bundles: str | None = None) -> None:
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("npm is required to build the Tauri bundle")
    command = [npm, "run", "build", "--"]
    if bundles:
        command.extend(["--bundles", bundles])
    environment = os.environ.copy()
    environment["CI"] = "true"
    subprocess.run(
        command,
        check=True,
        cwd=DESKTOP_DIR,
        env=environment,
    )


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
