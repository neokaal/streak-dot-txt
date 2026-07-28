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
streak_core - Core implementation for the streak.txt format.
Contains data models, file operations, and business logic shared between CLI and GUI.

author: Abhishek Mishra
date: 18/06/2025
"""

from .models import DailyTick, Streak
from .file_operations import StreakFileManager
from .statistics import StreakStatsCalculator
from .display import TerminalDisplay
from .constants import (
    DEFAULT_STREAKS_DIR,
    SUPPORTED_TICK_TYPES,
    default_streaks_dir,
    resolve_streaks_dir,
)
from .repository import StreakRepository, StreakNotFoundError, InvalidStreakIdError
from .services import StreakService, DuplicateTickError
from .version import __version__

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
