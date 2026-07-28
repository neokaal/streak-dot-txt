"""
Startup script for the Streak API server
"""

import uvicorn

if __name__ == "__main__":
    print("Starting Streak API server...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        "streak_api.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
