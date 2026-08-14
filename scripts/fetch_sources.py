"""Fetch and verify Lua and LuaFileSystem C sources into local build/ directory."""

from __future__ import annotations

import hashlib
import os
import tarfile
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT_DIR / "build"

DEPENDENCIES = [
    {
        "name": "Lua 5.4.8",
        "url": "https://lua.org/ftp/lua-5.4.8.tar.gz",
        "tar_name": "lua-5.4.8.tar.gz",
        "target_dir": BUILD_DIR / "lua-5.4.8",
        "check_file": BUILD_DIR / "lua-5.4.8" / "src" / "lua.h",
        "expected_size": 374332,
        "expected_sha256": "4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae",
    },
    {
        "name": "LuaFileSystem 1.9.0",
        "url": "https://github.com/lunarmodules/luafilesystem/archive/refs/tags/v1_9_0.tar.gz",
        "tar_name": "v1_9_0.tar.gz",
        "target_dir": BUILD_DIR / "luafilesystem-1_9_0",
        "check_file": BUILD_DIR / "luafilesystem-1_9_0" / "src" / "lfs.c",
        "expected_size": 29279,
        "expected_sha256": "1142c1876e999b3e28d1c236bf21ffd9b023018e336ac25120fb5373aade1450",
    },
]


def verify_file(file_path: Path, expected_size: int, expected_sha256: str) -> None:
    actual_size = file_path.stat().st_size
    if actual_size != expected_size:
        raise ValueError(
            f"Size mismatch for {file_path.name}: expected {expected_size} bytes, got {actual_size} bytes"
        )

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    actual_sha256 = hasher.hexdigest()
    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"SHA256 mismatch for {file_path.name}:\n"
            f"  Expected: {expected_sha256}\n"
            f"  Actual:   {actual_sha256}"
        )


def fetch_and_verify_sources() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    for dep in DEPENDENCIES:
        name = dep["name"]
        check_file: Path = dep["check_file"]
        target_dir: Path = dep["target_dir"]

        if check_file.exists():
            print(f"{name} source already available at {target_dir}")
            continue

        tar_path = BUILD_DIR / dep["tar_name"]
        url = dep["url"]

        print(f"Fetching {name} source from {url}...")
        urllib.request.urlretrieve(url, tar_path)

        print(f"Verifying {name} size and SHA256 checksum...")
        verify_file(tar_path, dep["expected_size"], dep["expected_sha256"])

        print(f"Extracting {name} source...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=BUILD_DIR, filter="data")

        if tar_path.exists():
            os.remove(tar_path)

        print(f"{name} ready at {target_dir}")


if __name__ == "__main__":
    fetch_and_verify_sources()
