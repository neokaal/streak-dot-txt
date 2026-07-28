import os
import sys

import pytest

from desktop import package_release, package_sidecar
from scripts.set_version import set_version


def test_sidecar_builder_uses_the_active_python_and_platform_data_separator(
    monkeypatch,
):
    calls = []
    monkeypatch.setattr(
        package_sidecar.subprocess,
        "run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    result = package_sidecar.build_sidecar()

    command, options = calls[0]
    assert command[:3] == [sys.executable, "-m", "PyInstaller"]
    assert "--onedir" in command
    assert any(
        argument.endswith(f"{os.pathsep}streak_api/templates")
        for argument in command
    )
    assert options["check"] is True
    expected_suffix = ".exe" if os.name == "nt" else ""
    assert result == (
        package_sidecar.DESKTOP_DIR
        / "dist"
        / "streak-server"
        / f"streak-server{expected_suffix}"
    )


def test_release_builder_copies_the_target_sidecar_and_forwards_bundle_choice(
    tmp_path,
    monkeypatch,
):
    desktop_directory = tmp_path / "desktop"
    sidecar_directory = tmp_path / "built-sidecar"
    sidecar_directory.mkdir()
    sidecar = sidecar_directory / (
        "streak-server.exe" if os.name == "nt" else "streak-server"
    )
    sidecar.write_bytes(b"sidecar")
    (sidecar_directory / "support-library").write_bytes(b"support")
    calls = []

    monkeypatch.setattr(package_release, "DESKTOP_DIR", desktop_directory)
    monkeypatch.setattr(package_release, "build_sidecar", lambda: sidecar)
    monkeypatch.setattr(package_release.shutil, "which", lambda _: "npm")
    monkeypatch.setattr(
        package_release.subprocess,
        "run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    package_release.build_release("app")

    copied_directory = (
        desktop_directory
        / "src-tauri"
        / "resources"
        / "sidecar"
    )
    assert (copied_directory / sidecar.name).read_bytes() == b"sidecar"
    assert (copied_directory / "support-library").read_bytes() == b"support"
    assert calls == [
        (
            ["npm", "run", "build", "--", "--bundles", "app"],
            {"check": True, "cwd": desktop_directory},
        )
    ]


def test_version_updater_rejects_non_semantic_versions_without_writing():
    with pytest.raises(ValueError, match="semantic version"):
        set_version("release-next")
