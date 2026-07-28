#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="$project_root/desktop/dist"
data_separator=":"
if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OS:-}" == Windows_NT ]]; then
  data_separator=";"
fi
"$project_root/.env/bin/pyinstaller" --noconfirm --clean --onefile \
  --name streak-server --paths "$project_root" \
  --hidden-import streak_api.main \
  --add-data "$project_root/streak_api/templates${data_separator}streak_api/templates" \
  --add-data "$project_root/streak_api/static${data_separator}streak_api/static" \
  --distpath "$output_dir" --workpath "$project_root/build/desktop-sidecar" \
  "$project_root/desktop/server.py"
