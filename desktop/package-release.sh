#!/usr/bin/env bash
# Build a distributable installer for the current OS and architecture.
set -euo pipefail

desktop_dir="$(cd "$(dirname "$0")" && pwd)"
target_triple="${1:-$(rustc -vV | sed -n 's/^host: //p')}"

cd "$desktop_dir"
./package-sidecar.sh

sidecar_source="dist/streak-server"
sidecar_destination="src-tauri/binaries/streak-server-$target_triple"
if [[ -f "$sidecar_source.exe" ]]; then
  sidecar_source="$sidecar_source.exe"
  sidecar_destination="$sidecar_destination.exe"
fi

mkdir -p src-tauri/binaries
cp "$sidecar_source" "$sidecar_destination"
npm run build
