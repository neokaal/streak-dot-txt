import os
from pathlib import Path
import sys

import pytest

from desktop import measure_startup, package_release, package_sidecar
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
    assert ("--hide-console" in command) is (os.name == "nt")
    for excluded_module in (
        "PIL",
        "rich",
        "tkinter",
        "uvloop",
        "watchfiles",
        "websockets",
    ):
        assert excluded_module in command
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


def test_windows_sidecar_hides_its_console_without_removing_standard_streams():
    command = package_sidecar.pyinstaller_command(windows=True)

    console_option = command.index("--hide-console")
    assert command[console_option : console_option + 2] == [
        "--hide-console",
        "hide-early",
    ]
    assert "--noconsole" not in command


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
    command, options = calls[0]
    assert command == [
        "npm",
        "run",
        "build",
        "--",
        "--bundles",
        "app",
    ]
    assert options["check"] is True
    assert options["cwd"] == desktop_directory
    assert options["env"]["CI"] == "true"


def test_release_builder_can_prepare_the_sidecar_without_running_tauri(
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

    monkeypatch.setattr(package_release, "DESKTOP_DIR", desktop_directory)
    monkeypatch.setattr(package_release, "build_sidecar", lambda: sidecar)

    destination = package_release.prepare_sidecar_resource()

    assert destination == (
        desktop_directory / "src-tauri" / "resources" / "sidecar"
    )
    assert (destination / sidecar.name).read_bytes() == b"sidecar"


def test_version_updater_rejects_non_semantic_versions_without_writing():
    with pytest.raises(ValueError, match="semantic version"):
        set_version("release-next")


def test_startup_measurement_uses_an_isolated_streak_directory(
    tmp_path,
    monkeypatch,
):
    sidecar = tmp_path / "sidecar"
    sidecar.write_bytes(b"binary")
    captured = {}

    class FakeProcess:
        returncode = None

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            return self.returncode

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self):
            return b"test-token"

    def fake_popen(command, **options):
        captured["command"] = command
        captured["environment"] = options["env"]
        return FakeProcess()

    monkeypatch.setattr(measure_startup, "available_port", lambda: 8765)
    monkeypatch.setattr(
        measure_startup.secrets,
        "token_hex",
        lambda _: "test-token",
    )
    monkeypatch.setattr(measure_startup.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        measure_startup.urllib.request,
        "urlopen",
        lambda request, timeout: FakeResponse(),
    )

    elapsed = measure_startup.measure_startup(sidecar)

    assert elapsed >= 0
    assert captured["command"] == [str(sidecar)]
    streaks_directory = Path(captured["environment"]["STREAKS_DIR"])
    assert streaks_directory.name == "streaks"
    assert "streak-startup-" in str(streaks_directory)
