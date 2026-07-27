"""Entrypoint bundled as the local desktop API sidecar."""

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "streak_api.main:app",
        host="127.0.0.1",
        port=int(os.environ.get("STREAK_PORT", "8000")),
        log_level="warning",
    )
