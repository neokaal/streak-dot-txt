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
Statistics calculations for the streak.txt format.
"""

import datetime


class StreakStatsCalculator:
    """
    Calculates statistics for streak objects.
    """

    @staticmethod
    def calculate_stats(streak):
        """
        Calculate the stats for the streak

        total_days - total days the streak has been active, first tick to current date
        ticked_days - total days or weeks the streak has been ticked
        unticked_days - total days or weeks the streak has not been ticked (total_days - ticked_days)
        current_streak - current streak of ticked days or weeks
        longest_streak - longest streak of ticked days or weeks
        tick_average - percentage of days/weeks that have been ticked
        """
        today = datetime.date.today()
        current_period = StreakStatsCalculator._normalize_date(streak, today)
        tick_dates = {
            StreakStatsCalculator._normalize_date(streak, tick.get_date())
            for tick in streak.ticks
            if StreakStatsCalculator._normalize_date(streak, tick.get_date()) <= current_period
        }

        if not tick_dates:
            streak.stats = {
                "total_days": 0,
                "ticked_days": 0,
                "unticked_days": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "tick_average": 0
            }
            return streak.stats

        first_period = min(tick_dates)
        streak.stats["total_days"] = (
            (current_period - first_period).days // streak.period
        ) + 1
        streak.stats["ticked_days"] = len(tick_dates)
        streak.stats["unticked_days"] = (
            streak.stats["total_days"] - streak.stats["ticked_days"]
        )
        
        # Calculate current and longest streaks
        current_streak, longest_streak = StreakStatsCalculator._calculate_streaks(
            tick_dates,
            current_period,
            streak.period,
        )
        streak.stats["current_streak"] = current_streak
        streak.stats["longest_streak"] = longest_streak
        
        # Calculate tick average
        streak.stats["tick_average"] = (
            streak.stats["ticked_days"] / streak.stats["total_days"]
            if streak.stats["total_days"] > 0 else 0
        )

        return streak.stats

    @staticmethod
    def _normalize_date(streak, tick_date):
        if streak.tick == "Daily":
            return tick_date
        if streak.tick == "Weekly":
            return tick_date - datetime.timedelta(days=tick_date.weekday())
        raise ValueError(f"Unsupported tick type: {streak.tick}")

    @staticmethod
    def _calculate_streaks(tick_dates, current_period, period):
        """
        Calculate current and longest streaks for the given streak object.
        Returns (current_streak, longest_streak) tuple.
        """
        longest_streak = 0
        run = 0
        previous = None

        for tick_date in sorted(tick_dates):
            if previous is not None and (tick_date - previous).days == period:
                run += 1
            else:
                run = 1
            longest_streak = max(longest_streak, run)
            previous = tick_date

        current_streak = run if previous == current_period else 0
        return current_streak, longest_streak
