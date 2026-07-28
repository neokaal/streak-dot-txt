#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
"$project_root/.env/bin/python" "$project_root/desktop/package_release.py" "$@"
