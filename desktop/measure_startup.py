"""Measure packaged sidecar readiness without reading personal streak files."""

from __future__ import annotations

import argparse
import os
import secrets
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIDECAR = (
    PROJECT_ROOT
    / "desktop"
    / "dist"
    / "streak-server"
    / ("streak-server.exe" if os.name == "nt" else "streak-server")
)


def available_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def measure_startup(sidecar: Path, timeout: float = 30) -> float:
    if not sidecar.is_file():
        raise FileNotFoundError(sidecar)

    token = secrets.token_hex(16)
    port = available_port()
    with tempfile.TemporaryDirectory(prefix="streak-startup-") as directory:
        environment = os.environ.copy()
        environment.update(
            STREAK_INSTANCE_TOKEN=token,
            STREAK_PORT=str(port),
            STREAKS_DIR=str(Path(directory) / "streaks"),
        )
        started_at = time.perf_counter()
        process = subprocess.Popen(
            [str(sidecar)],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            health_url = (
                f"http://127.0.0.1:{port}/desktop-health?token={token}"
            )
            deadline = started_at + timeout
            while time.perf_counter() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"Sidecar exited with status {process.returncode}"
                    )
                try:
                    with urllib.request.urlopen(
                        health_url,
                        timeout=0.2,
                    ) as response:
                        if response.read().decode() == token:
                            return time.perf_counter() - started_at
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(0.02)
            raise TimeoutError(f"Sidecar was not ready within {timeout} seconds")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sidecar",
        nargs="?",
        type=Path,
        default=DEFAULT_SIDECAR,
    )
    parser.add_argument("--runs", type=int, default=3)
    arguments = parser.parse_args()
    measurements = [
        measure_startup(arguments.sidecar) for _ in range(arguments.runs)
    ]
    for index, measurement in enumerate(measurements, start=1):
        print(f"run {index}: {measurement:.3f}s")
    print(f"best: {min(measurements):.3f}s")


if __name__ == "__main__":
    main()
