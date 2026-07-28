"""Entrypoint bundled as the local desktop API sidecar."""

import os

import uvicorn


if __name__ == "__main__":
    port = int(os.environ["STREAK_PORT"])
    if not os.environ.get("STREAK_INSTANCE_TOKEN"):
        raise RuntimeError("STREAK_INSTANCE_TOKEN is required for desktop startup")
    uvicorn.run(
        "streak_api.main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
