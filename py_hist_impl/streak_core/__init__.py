"""Public, lazily loaded API for the streak.txt core package."""

from __future__ import annotations

from importlib import import_module

from .constants import (
    DEFAULT_STREAKS_DIR,
    SUPPORTED_TICK_TYPES,
    default_streaks_dir,
    resolve_streaks_dir,
)
from .version import __version__


_LAZY_EXPORTS = {
    "DailyTick": (".models", "DailyTick"),
    "DuplicateTickError": (".services", "DuplicateTickError"),
    "InvalidStreakIdError": (".repository", "InvalidStreakIdError"),
    "Streak": (".models", "Streak"),
    "StreakFileManager": (".file_operations", "StreakFileManager"),
    "StreakNotFoundError": (".repository", "StreakNotFoundError"),
    "StreakRepository": (".repository", "StreakRepository"),
    "StreakService": (".services", "StreakService"),
    "StreakStatsCalculator": (".statistics", "StreakStatsCalculator"),
    "TerminalDisplay": (".display", "TerminalDisplay"),
}


def __getattr__(name):
    try:
        module_name, attribute_name = _LAZY_EXPORTS[name]
    except KeyError as error:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from error
    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value


__all__ = [
    "DEFAULT_STREAKS_DIR",
    "DailyTick",
    "DuplicateTickError",
    "InvalidStreakIdError",
    "SUPPORTED_TICK_TYPES",
    "Streak",
    "StreakFileManager",
    "StreakNotFoundError",
    "StreakRepository",
    "StreakService",
    "StreakStatsCalculator",
    "TerminalDisplay",
    "__version__",
    "default_streaks_dir",
    "resolve_streaks_dir",
]
