"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date


class StreakCreate(BaseModel):
    name: str
    tick_type: str = "Daily"
    description: Optional[str] = None


class StreakUpdate(BaseModel):
    description: Optional[str] = None
    tick_type: Optional[str] = None


class TickResponse(BaseModel):
    tick_datetime_str: str
    tick_datetime: datetime
    year: int
    month: int
    day: int
    weekday: int


class StreakResponse(BaseModel):
    id: str
    name: str
    tick_type: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    ticks: List[TickResponse] = []
    stats: Dict[str, Any] = {}
    years: List[int] = []

    @classmethod
    def from_streak(cls, streak, streak_id: str):
        """Convert streak_core Streak object to API response"""
        tick_responses = []
        for tick in streak.ticks:
            tick_responses.append(
                TickResponse(
                    tick_datetime_str=tick.tick_datetime_str,
                    tick_datetime=tick.tick_datetime,
                    year=tick.get_year(),
                    month=tick.get_month(),
                    day=tick.get_day(),
                    weekday=tick.get_weekday(),
                )
            )

        return cls(
            id=streak_id,
            name=streak.name or "Unnamed Streak",
            tick_type=streak.tick,
            description=streak.metadata.get("description"),
            metadata=streak.metadata,
            ticks=tick_responses,
            stats=streak.stats,
            years=streak.get_years(),
        )


class TickCreate(BaseModel):
    tick_datetime_str: str


class StatusResponse(BaseModel):
    message: str
    success: bool = True
