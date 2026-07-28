#!/usr/bin/env bash
# Start the local API and Tauri development window as one process group.
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
server_pid=""

cleanup() {
  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid"
    wait "$server_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

cd "$project_root"
STREAK_PORT=8000 .env/bin/python -m uvicorn streak_api.main:app --host 127.0.0.1 --port 8000 --log-level warning &
server_pid=$!

for _ in {1..50}; do
  if curl --silent --fail http://127.0.0.1:8000/health >/dev/null; then
    cd desktop
    npm run dev
    exit $?
  fi
  sleep 0.1
done

echo "Streak.txt server did not start on http://127.0.0.1:8000" >&2
exit 1
