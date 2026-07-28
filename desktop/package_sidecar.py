"""Build the Python desktop sidecar with the active interpreter."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DIR = PROJECT_ROOT / "desktop"


def pyinstaller_command(*, windows: bool | None = None) -> list[str]:
    if windows is None:
        windows = os.name == "nt"
    output_directory = DESKTOP_DIR / "dist"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "streak-server",
        "--paths",
        str(PROJECT_ROOT),
        "--hidden-import",
        "streak_api.main",
        "--exclude-module",
        "PIL",
        "--exclude-module",
        "rich",
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "uvloop",
        "--exclude-module",
        "watchfiles",
        "--exclude-module",
        "websockets",
        "--add-data",
        f"{PROJECT_ROOT / 'streak_api' / 'templates'}{os.pathsep}streak_api/templates",
        "--add-data",
        f"{PROJECT_ROOT / 'streak_api' / 'static'}{os.pathsep}streak_api/static",
        "--distpath",
        str(output_directory),
        "--workpath",
        str(PROJECT_ROOT / "build" / "desktop-sidecar"),
        str(DESKTOP_DIR / "server.py"),
    ]
    if windows:
        command.insert(5, "--noconsole")
    return command


def build_sidecar() -> Path:
    command = pyinstaller_command()
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)
    suffix = ".exe" if os.name == "nt" else ""
    return DESKTOP_DIR / "dist" / "streak-server" / f"streak-server{suffix}"


if __name__ == "__main__":
    build_sidecar()
