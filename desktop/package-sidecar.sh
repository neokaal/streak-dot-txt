#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="$project_root/desktop/dist"
"$project_root/.env/bin/pyinstaller" --noconfirm --clean --onefile \
  --name streak-server --paths "$project_root" \
  --distpath "$output_dir" --workpath "$project_root/build/desktop-sidecar" \
  "$project_root/desktop/server.py"
