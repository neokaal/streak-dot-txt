"""Run the local API and Tauri development window as one process group."""

from __future__ import annotations

import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DIR = PROJECT_ROOT / "desktop"
PORT = 8000


def wait_until_ready(server: subprocess.Popen, token: str) -> None:
    health_url = f"http://127.0.0.1:{PORT}/desktop-health?token={token}"
    for _ in range(100):
        exit_code = server.poll()
        if exit_code is not None:
            raise RuntimeError(f"Local server exited with status {exit_code}")
        try:
            with urllib.request.urlopen(health_url, timeout=0.2) as response:
                if response.read().decode() == token:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.1)
    raise TimeoutError(f"Streak.txt server did not start on port {PORT}")


def stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> None:
    token = secrets.token_hex(16)
    environment = os.environ.copy()
    environment.update(
        STREAK_PORT=str(PORT),
        STREAK_INSTANCE_TOKEN=token,
    )
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "streak_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(PORT),
            "--log-level",
            "warning",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
    )
    try:
        wait_until_ready(server, token)
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if not npm:
            raise RuntimeError("npm is required to run the Tauri window")
        subprocess.run([npm, "run", "dev"], check=True, cwd=DESKTOP_DIR)
    finally:
        stop_process(server)


if __name__ == "__main__":
    main()
