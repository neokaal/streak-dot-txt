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
streakdottxt.py - Reference implementation of the streak.txt format.
A command line tool to manage daily streaks all stored in text files.

author: Abhishek Mishra
date: 05/01/2025
"""
import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import box

from streak_core import (
    DEFAULT_STREAKS_DIR,
    DailyTick,
    Streak as CoreStreak,
    StreakFileManager,
    StreakRepository,
    StreakService,
    StreakStatsCalculator,
    TerminalDisplay,
)


# Enhanced Streak class that adds file I/O and statistics calculation
class EnhancedStreak(CoreStreak):
    """
    Enhanced Streak class that combines the core Streak model with file operations
    and statistics calculations for backward compatibility.
    """

    def __init__(self, streak_file):
        # Initialize base streak first
        super().__init__()
        self.streak_file = streak_file
        
        # Load from file using the file manager
        loaded_streak = StreakFileManager.load_from_file(streak_file)
        
        # Copy all attributes from loaded streak
        self.name = loaded_streak.name
        self.tick = loaded_streak.tick
        self.metadata = loaded_streak.metadata
        self.ticks = loaded_streak.ticks
        self.period = loaded_streak.period
        self.years = loaded_streak.years
        self.stats = loaded_streak.stats
        
        # Calculate statistics
        StreakStatsCalculator.calculate_stats(self)

    def mark_today(self):
        """
        Mark today or this week as ticked, but only if it is not already ticked
        """
        result = super().mark_today()
        if result:
            self.write_streak()
            # Recalculate stats after adding tick
            StreakStatsCalculator.calculate_stats(self)
        return result

    def write_streak(self):
        """
        Write the streak to the file
        """
        StreakFileManager.save_to_file(self, self.streak_file)

    def calculate_stats(self):
        """
        Calculate the stats for the streak
        """
        StreakStatsCalculator.calculate_stats(self)

# Backward compatibility - keep the original Streak name
Streak = EnhancedStreak


# TerminalDisplay is now imported from streak_core


@click.group(
    help="The streak command line tool helps you keep track of your daily streaks."
)
@click.option("--dir", default=DEFAULT_STREAKS_DIR, help="Directory to store streaks")
@click.pass_context
def streakdottxt(ctx, dir):
    ctx.ensure_object(dict)
    ctx.obj["dir"] = dir


def _service(directory):
    return StreakService(StreakRepository(directory))


def _resolve_streak(directory, file_path=None, name=None):
    if file_path:
        path = Path(file_path).expanduser().resolve()
        if not path.name.startswith("streak-") or path.suffix != ".txt":
            raise click.ClickException(
                "A streak file must use the name streak-<id>.txt"
            )
        service = _service(path.parent)
        streak_id = path.stem.removeprefix("streak-")
        return service, streak_id, service.get_streak(streak_id)

    if name:
        service = _service(directory)
        query = name.casefold()
        matches = [
            (streak_id, streak)
            for streak_id, streak in service.list_streaks()
            if query in streak_id.casefold()
            or query in (streak.name or "").casefold()
        ]
        if not matches:
            raise click.ClickException(f"No streak found matching {name!r}")
        if len(matches) > 1:
            choices = ", ".join(streak_id for streak_id, _ in matches)
            raise click.ClickException(
                f"Multiple streaks match {name!r}: {choices}"
            )
        streak_id, streak = matches[0]
        return service, streak_id, streak

    raise click.ClickException("Provide either --file or --name")


@streakdottxt.command(help="View the streak")
@click.option("-f", "--file", help="Streak file to view")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def view(ctx, file, name):
    _, _, streak = _resolve_streak(ctx.obj["dir"], file, name)
    display = TerminalDisplay(streak)
    display.display_all()


def mark_streak(dir, file, name):
    service, streak_id, streak = _resolve_streak(dir, file, name)
    click.echo(f"Streak: {streak.name}")
    changed = service.tick_today(streak_id)
    click.echo("Tick added" if changed else "Already ticked")


@streakdottxt.command(help="Mark today's tick")
@click.option("-f", "--file", help="Streak file to mark")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def mark(ctx, file, name):
    dir = ctx.obj["dir"]
    mark_streak(dir, file, name)


@streakdottxt.command(help="Tick today's tick (same as mark)")
@click.option("-f", "--file", help="Streak file to tick")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def tick(ctx, file, name):
    dir = ctx.obj["dir"]
    mark_streak(dir, file, name)


@streakdottxt.command(help="Create a new streak")
@click.option("-n", "--name", required=True, help="Name of the new streak")
@click.pass_context
def new(ctx, name):
    try:
        streak_id, _ = _service(ctx.obj["dir"]).create_streak(name)
        path = StreakRepository(ctx.obj["dir"]).path_for(streak_id)
        click.echo(f"Streak {name!r} created at {path}")
    except (FileExistsError, ValueError) as error:
        raise click.ClickException(str(error)) from error


@streakdottxt.command(help="List all the streaks in the directory")
@click.pass_context
def list(ctx):
    streaks = _service(ctx.obj["dir"]).list_streaks()
    if streaks:
        table = Table(title="Streaks", box=box.SIMPLE)
        table.add_column("Today")
        table.add_column("Name")
        table.add_column("Tick")
        table.add_column("Longest Streak")
        table.add_column("Current Streak")
        table.add_column("Tick Average")

        for _, streak in streaks:
            today = datetime.datetime.now().date()
            today_status = "✓" if streak.is_current_period_ticked(today) else "✖"
            table.add_row(
                today_status,
                streak.name,
                streak.tick,
                str(streak.stats["longest_streak"]),
                str(streak.stats["current_streak"]),
                f"{streak.stats['tick_average'] * 100:.0f}%",
            )

        console = Console()
        console.print(table)
    else:
        click.echo("No streaks found")


def get_streak_from_file_or_name(dir, file, name):
    """Backward-compatible lookup routed through the unified service."""
    return _resolve_streak(dir, file, name)[2]


if __name__ == "__main__":
    streakdottxt()
