# MIT License

# Copyright (c) 2025 Abhishek Mishra (neolateral.in)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Core data models for the streak.txt format.
"""

import datetime
import dateutil.parser
from .constants import TICK_PERIODS


class DailyTick:
    """
    DailyTick class represents a tick for a daily streak.
    It has a tick_datetime_str which is the date in ISO8601 format
    and a tick_datetime which is a datetime object parsed from the tick_datetime_str
    """

    def __init__(self, tick_datetime_str):
        self.tick_datetime_str = tick_datetime_str
        # parse ISO8601 date using dateutil.parser
        self.tick_datetime = dateutil.parser.parse(tick_datetime_str)

    def get_year(self):
        return self.tick_datetime.year

    def get_month(self):
        return self.tick_datetime.month

    def get_day(self):
        return self.tick_datetime.day

    def get_weekday(self):
        return self.tick_datetime.weekday()

    def get_week_in_month(self):
        # get the week in the month
        return (self.tick_datetime.day - 1) // 7 + 1

    def get_week_in_year(self):
        # get the week in the year
        return self.tick_datetime.isocalendar()[1]

    def get_iso_week(self):
        iso_calendar = self.tick_datetime.isocalendar()
        return iso_calendar.year, iso_calendar.week

    def get_date(self):
        return self.tick_datetime.date()

    def __str__(self):
        return str(self.tick_datetime)


class Streak:
    """
    Streak class represents a streak.

    Core data model for streak management containing ticks, metadata, and statistics.

    self.period: represents the period of the tick in number of intervals.
                if the task is done once per day then period is 1
                if the task is done once per week then period is 7
                if the task is done once per month then period is the length of the month
    """

    def __init__(self, name=None, tick_type="Daily"):
        self.name = name
        self.tick = tick_type
        self.metadata = {}
        self.ticks = []
        self.years = []
        self.stats = {
            "total_days": 0,
            "ticked_days": 0,
            "unticked_days": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "tick_average": 0
        }
        
        if self.tick not in TICK_PERIODS:
            raise ValueError(f"Unsupported tick type: {self.tick}")
        self.period = TICK_PERIODS[self.tick]

    def mark_today(self):
        """
        Mark today or this week as ticked, but only if it is not already ticked
        """
        today = datetime.datetime.now()
        if self.is_current_period_ticked(today.date()):
            return False

        if self.tick == "Daily":
            today_tick = DailyTick(today.isoformat())
            self.ticks.append(today_tick)
            return True
        elif self.tick == "Weekly":
            start_of_week = today - datetime.timedelta(days=today.weekday())
            week_tick = DailyTick(start_of_week.isoformat())
            self.ticks.append(week_tick)
            return True

    def is_current_period_ticked(self, reference_date=None):
        """Return whether the daily or weekly period containing a date is ticked."""
        reference_date = reference_date or datetime.date.today()
        if self.tick == "Daily":
            return any(tick.get_date() == reference_date for tick in self.ticks)
        if self.tick == "Weekly":
            iso_calendar = reference_date.isocalendar()
            target_week = (iso_calendar.year, iso_calendar.week)
            return any(tick.get_iso_week() == target_week for tick in self.ticks)
        raise ValueError(f"Unsupported tick type: {self.tick}")

    def get_years(self):
        """
        Get the years that the streak has been active
        """
        self.years = []
        for tick in self.ticks:
            year = tick.get_year()
            if year not in self.years:
                self.years.append(year)
        return self.years

    def add_tick(self, tick_datetime_str):
        """
        Add a new tick to the streak
        """
        tick = DailyTick(tick_datetime_str)
        self.ticks.append(tick)

    def set_metadata(self, key, value):
        """
        Set metadata for the streak
        """
        self.metadata[key] = value
        if key == "name":
            self.name = value
        elif key == "tick":
            if value not in TICK_PERIODS:
                raise ValueError(f"Unsupported tick type: {value}")
            self.tick = value
            self.period = TICK_PERIODS[value]
