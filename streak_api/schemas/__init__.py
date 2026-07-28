"""Pydantic schemas for API request and response models."""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, StringConstraints


StreakName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
SingleLine = Annotated[str, StringConstraints(max_length=1_000, pattern=r"^[^\r\n]*$")]
TickType = Literal["Daily", "Weekly"]


class StreakCreate(BaseModel):
    name: StreakName
    tick_type: TickType = "Daily"
    description: SingleLine | None = None


class StreakUpdate(BaseModel):
    description: SingleLine | None = None
    tick_type: TickType | None = None


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
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    ticks: list[TickResponse] = Field(default_factory=list)
    stats: dict[str, Any] = Field(default_factory=dict)
    years: list[int] = Field(default_factory=list)

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
    tick_datetime_str: Annotated[str, StringConstraints(min_length=1, max_length=100)]


class StatusResponse(BaseModel):
    message: str
    success: bool = True
