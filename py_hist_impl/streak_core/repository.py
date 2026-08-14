"""Safe persistence for streak.txt files."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .file_operations import StreakFileManager


class StreakNotFoundError(LookupError):
    pass


class InvalidStreakIdError(ValueError):
    pass


class StreakRepository:
    """Owns filename resolution and durable persistence for one streak directory."""

    CONFIG_FILENAME = "streaks-config.json"

    def __init__(self, directory: str | Path):
        self.directory = Path(directory).expanduser()

    @staticmethod
    def slugify(name: str) -> str:
        try:
            return StreakFileManager.slugify_name(name)
        except ValueError as error:
            raise InvalidStreakIdError(str(error)) from error

    def _validate_id(self, streak_id: str) -> str:
        # IDs are incorporated into a filename. Existing files can have names
        # made before slug IDs existed, so retain every single safe path
        # component rather than silently hiding a user's streak.
        if not streak_id or streak_id in {".", ".."} or "/" in streak_id or "\\" in streak_id or "\x00" in streak_id:
            raise InvalidStreakIdError("Streak ID must be a single filename component")
        return streak_id

    def path_for(self, streak_id: str) -> Path:
        return self.directory / f"streak-{self._validate_id(streak_id)}.txt"

    @property
    def config_path(self) -> Path:
        return self.directory / self.CONFIG_FILENAME

    def _file_ids(self) -> list[str]:
        return sorted(path.stem.removeprefix("streak-") for path in self.directory.glob("streak-*.txt"))

    def _read_config(self) -> dict:
        if not self.config_path.is_file():
            return {}
        try:
            config = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return config if isinstance(config, dict) else {}

    def _write_order(self, streak_ids: list[str]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        config = self._read_config()
        config.setdefault("version", 1)
        config["order"] = [self._validate_id(streak_id) for streak_id in streak_ids]
        fd, temporary_name = tempfile.mkstemp(prefix=f".{self.CONFIG_FILENAME}.", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, indent=2)
                config_file.write("\n")
            os.replace(temporary_name, self.config_path)
        except Exception:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
            raise

    def list_ids(self) -> list[str]:
        if not self.directory.exists():
            return []
        file_ids = self._file_ids()
        if not self.config_path.is_file():
            self._write_order(file_ids)
            return file_ids

        config = self._read_config()
        available = set(file_ids)
        ordered = []
        order_lines = config.get("order", [])
        if not isinstance(order_lines, list):
            order_lines = []

        for streak_id in order_lines:
            if isinstance(streak_id, str) and streak_id in available and streak_id not in ordered:
                ordered.append(streak_id)
        ordered.extend(streak_id for streak_id in file_ids if streak_id not in ordered)

        if ordered != order_lines:
            self._write_order(ordered)
        return ordered

    def load(self, streak_id: str):
        path = self.path_for(streak_id)
        if not path.is_file():
            raise StreakNotFoundError(streak_id)
        return StreakFileManager.load_from_file(str(path))

    def create(self, name: str, tick_type: str, description: str | None = None):
        streak_id = self.slugify(name)
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.path_for(streak_id)
        if path.exists():
            raise FileExistsError(f"Streak already exists: {streak_id}")
        existing_order = self.list_ids()
        metadata = {"description": description} if description else None
        StreakFileManager.create_new_streak_file(
            str(self.directory),
            name,
            tick_type,
            metadata=metadata,
        )
        self._write_order([*existing_order, streak_id])
        return streak_id, self.load(streak_id)

    def save(self, streak, streak_id: str) -> None:
        path = self.path_for(streak_id)
        if not path.is_file():
            raise StreakNotFoundError(streak_id)
        self.directory.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=self.directory)
        os.close(fd)
        try:
            StreakFileManager.save_to_file(streak, temporary_name)
            os.replace(temporary_name, path)
        except Exception:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
            raise

    def archive(self, streak_id: str) -> Path:
        path = self.path_for(streak_id)
        if not path.is_file():
            raise StreakNotFoundError(streak_id)
        existing_order = self.list_ids()
        archive = self.directory / "archive"
        archive.mkdir(exist_ok=True)
        destination = archive / path.name
        counter = 1
        while destination.exists():
            destination = archive / f"{path.stem}.{counter}{path.suffix}"
            counter += 1
        os.replace(path, destination)
        self._write_order([item for item in existing_order if item != streak_id])
        return destination
