"""Update every checked-in Streak.txt release version."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    contents = path.read_text()
    updated, count = re.subn(pattern, replacement, contents, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected one version marker in {path}")
    path.write_text(updated)


def set_version(version: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        raise ValueError("Version must use semantic version syntax")

    replace_once(
        PROJECT_ROOT / "streak_core" / "version.py",
        r'^__version__ = "[^"]+"$',
        f'__version__ = "{version}"',
    )
    replace_once(
        PROJECT_ROOT / "desktop" / "src-tauri" / "Cargo.toml",
        r'^version = "[^"]+"$',
        f'version = "{version}"',
    )
    replace_once(
        PROJECT_ROOT / "desktop" / "src-tauri" / "Cargo.lock",
        r'(?ms)(\[\[package\]\]\nname = "streak-txt"\nversion = ")[^"]+(")',
        rf"\g<1>{version}\g<2>",
    )

    for relative_path in (
        Path("desktop/package.json"),
        Path("desktop/package-lock.json"),
        Path("desktop/src-tauri/tauri.conf.json"),
    ):
        path = PROJECT_ROOT / relative_path
        data = json.loads(path.read_text())
        data["version"] = version
        if relative_path.name == "package-lock.json":
            data["packages"][""]["version"] = version
        path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="semantic version, for example 0.2.0")
    arguments = parser.parse_args()
    set_version(arguments.version)


if __name__ == "__main__":
    main()
