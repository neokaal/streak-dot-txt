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
Display utilities for the streak.txt format.
Provides terminal display functionality.
"""

import datetime
from rich.console import Console
from rich.table import Table
from rich import box


class TerminalDisplay:
    """
    TerminalDisplay class is used to display the streak information on the terminal.
    """

    def __init__(self, streak):
        self.streak = streak
        self.console = Console()

    def display_all(self):
        """
        Display all the information about the streak
        """
        self.display_streak_info()
        print()
        self.display_streak_stats()
        print()
        self.display_streak_calendar()

    def display_streak_info(self):
        """
        Display the streak information
        """
        print("Name [" + self.streak.name + "]")
        print("Tick [" + self.streak.tick + "]")

    def display_streak_stats(self):
        """
        Display the streak stats in a rich table
        """
        table = Table(title="Streak Stats", box=box.SIMPLE)
        table.add_column("Stat")
        table.add_column("Value")

        table.add_row("Total Days", str(self.streak.stats["total_days"]))
        table.add_row("Ticked Days", str(self.streak.stats["ticked_days"]))
        table.add_row("Unticked Days", str(self.streak.stats["unticked_days"]))
        table.add_row("Current Streak", str(self.streak.stats["current_streak"]))
        table.add_row("Longest Streak", str(self.streak.stats["longest_streak"]))
        table.add_row("Tick Average", f"{self.streak.stats['tick_average'] * 100:.0f}%")

        self.console.print(table)

    def display_streak_calendar(self):
        """
        Display the streak calendar till today's date only for the current year.

        The streak is displayed as a calendar on the terminal.

        Every month is displayed in a grid with the days of a month as cells
        and each line is a week.

        Each cell has a day number and a flag X or empty to indicate if the day
        is ticked or not.

        The first line of the month display has the month name,
        the second line has the days of the week, abbreviated to 3 letters.
        and spaced such that they are centered in the cell.
        """
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        # get the first day of the year
        first_day = datetime.datetime(current_year, 1, 1)
        # get the last day of the streak is today
        last_day = datetime.datetime(current_year, current_month, current_day)

        # draw all the months till the current month
        for month in range(1, current_month + 1):
            # get the first day of the month
            first_day = datetime.datetime(current_year, month, 1)
            # get the last day of the month
            last_day = datetime.datetime(
                current_year, month + 1, 1
            ) - datetime.timedelta(days=1)
            # draw the month
            self.draw_month(first_day, last_day)

    def draw_month(self, first_day, last_day):
        """
        Draw the month from first_day to last_day
        """
        month_name = first_day.strftime("%B")
        year = first_day.year
        first_weekday = first_day.weekday()
        num_days = (last_day - first_day).days + 1

        ticked_days = {
            tick.get_day()
            for tick in self.streak.ticks
            if tick.get_month() == first_day.month and tick.get_year() == first_day.year
        }

        table = Table(title=month_name + " " + str(year), box=box.SIMPLE)

        table.add_column("Sun", justify="center")
        table.add_column("Mon", justify="center")
        table.add_column("Tue", justify="center")
        table.add_column("Wed", justify="center")
        table.add_column("Thu", justify="center")
        table.add_column("Fri", justify="center")
        table.add_column("Sat", justify="center")

        week = [""] * first_weekday
        current_date = datetime.datetime.now().date()
        for day in range(1, num_days + 1):
            day_date = datetime.date(first_day.year, first_day.month, day)
            if day_date > current_date:
                day_display = f"[on dark_gray]{day:2} [-][/]"
            elif day_date == current_date:
                if day in ticked_days:
                    day_display = f"[bold][on green]{day:2} [✓][/][/bold]"
                else:
                    day_display = f"[bold][on blue]{day:2} [ ][/][/bold]"
            else:
                if day in ticked_days:
                    day_display = f"[on green]{day:2} [✓][/]"
                else:
                    day_display = f"[on red]{day:2} [✖][/]"
            week.append(day_display)
            if len(week) == 7:
                table.add_row(*week)
                week = []
        if week:
            table.add_row(*week)

        self.console.print(table)
