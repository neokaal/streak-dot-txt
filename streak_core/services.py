"""Application use cases shared by the API, UI, and CLI."""

from __future__ import annotations

from datetime import date

from .models import DailyTick
from .repository import StreakRepository
from .statistics import StreakStatsCalculator


class DuplicateTickError(ValueError):
    pass


class StreakService:
    def __init__(self, repository: StreakRepository):
        self.repository = repository

    def _hydrate(self, streak):
        streak.ticks.sort(key=lambda tick: tick.tick_datetime)
        StreakStatsCalculator.calculate_stats(streak)
        return streak

    def list_streaks(self):
        return [(streak_id, self._hydrate(self.repository.load(streak_id))) for streak_id in self.repository.list_ids()]

    def get_streak(self, streak_id: str):
        return self._hydrate(self.repository.load(streak_id))

    def create_streak(self, name: str, tick_type: str = "Daily", description: str | None = None):
        streak_id, streak = self.repository.create(name, tick_type)
        if description:
            streak.set_metadata("description", description)
            self.repository.save(streak, streak_id)
        return streak_id, self._hydrate(streak)

    def tick_today(self, streak_id: str) -> bool:
        streak = self.repository.load(streak_id)
        changed = streak.mark_today()
        if changed:
            self.repository.save(streak, streak_id)
        self._hydrate(streak)
        return changed

    def add_tick(self, streak_id: str, tick_datetime_str: str):
        streak = self.repository.load(streak_id)
        new_tick = DailyTick(tick_datetime_str)
        if any(tick.get_date() == new_tick.get_date() for tick in streak.ticks):
            raise DuplicateTickError(f"A tick already exists for {new_tick.get_date().isoformat()}")
        streak.ticks.append(new_tick)
        self.repository.save(streak, streak_id)
        return self._hydrate(streak)

    def update_streak(self, streak_id: str, description: str | None = None, tick_type: str | None = None):
        streak = self.repository.load(streak_id)
        if description is not None:
            streak.set_metadata("description", description)
        if tick_type is not None:
            if tick_type not in ("Daily", "Weekly"):
                raise ValueError("tick_type must be Daily or Weekly")
            streak.set_metadata("tick", tick_type)
            streak.period = 1 if tick_type == "Daily" else 7
        self.repository.save(streak, streak_id)
        return self._hydrate(streak)

    def archive_streak(self, streak_id: str):
        self.repository.archive(streak_id)
