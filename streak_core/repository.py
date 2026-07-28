"""Safe persistence for streak.txt files."""

from __future__ import annotations

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

    def list_ids(self) -> list[str]:
        if not self.directory.exists():
            return []
        return sorted(path.stem.removeprefix("streak-") for path in self.directory.glob("streak-*.txt"))

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
        metadata = {"description": description} if description else None
        StreakFileManager.create_new_streak_file(
            str(self.directory),
            name,
            tick_type,
            metadata=metadata,
        )
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
        archive = self.directory / "archive"
        archive.mkdir(exist_ok=True)
        destination = archive / path.name
        counter = 1
        while destination.exists():
            destination = archive / f"{path.stem}.{counter}{path.suffix}"
            counter += 1
        os.replace(path, destination)
        return destination
