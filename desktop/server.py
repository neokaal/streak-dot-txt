"""Entrypoint bundled as the local desktop API sidecar."""

import os
import sys

import uvicorn


def configure_sidecar_logging(*, windows: bool | None = None):
    if windows is None:
        windows = os.name == "nt"
    if not windows:
        return None

    log_path = os.environ.get("STREAK_LOG_PATH")
    if not log_path:
        raise RuntimeError("STREAK_LOG_PATH is required on Windows")
    stream = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = stream
    sys.stderr = stream
    return stream


if __name__ == "__main__":
    log_stream = configure_sidecar_logging()
    port = int(os.environ["STREAK_PORT"])
    if not os.environ.get("STREAK_INSTANCE_TOKEN"):
        raise RuntimeError("STREAK_INSTANCE_TOKEN is required for desktop startup")
    try:
        uvicorn.run(
            "streak_api.main:app",
            host="127.0.0.1",
            port=port,
            http="h11",
            loop="asyncio",
            log_level="warning",
            ws="none",
        )
    finally:
        if log_stream:
            log_stream.close()
