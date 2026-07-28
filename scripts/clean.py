"""Remove only known generated build and report directories."""

from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_PATHS = (
    PROJECT_ROOT / "build",
    PROJECT_ROOT / ".coverage",
    PROJECT_ROOT / "dist",
    PROJECT_ROOT / "htmlcov",
    PROJECT_ROOT / "desktop" / "dist",
    PROJECT_ROOT / "desktop" / "streak-server.spec",
    PROJECT_ROOT / "desktop" / "src-tauri" / "resources" / "sidecar",
    PROJECT_ROOT / "desktop" / "src-tauri" / "target",
    PROJECT_ROOT / "streak-server.spec",
)


def main() -> None:
    for path in GENERATED_PATHS:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"removed {path.relative_to(PROJECT_ROOT)}")
        elif path.exists():
            path.unlink()
            print(f"removed {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
