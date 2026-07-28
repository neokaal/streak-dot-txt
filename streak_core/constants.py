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
Constants for the streak.txt format implementation.
"""

import os
from pathlib import Path


def default_streaks_dir(home_dir: Path | None = None) -> Path:
    """Return the canonical, local-first streak directory: ``~/streaks``."""
    return (home_dir if home_dir is not None else Path.home()) / "streaks"


def resolve_streaks_dir(override: str | Path | None = None) -> Path:
    """Resolve an explicit override or the normal ``~/streaks`` location.

    ``STREAKS_DIR`` exists for development and deliberately selected alternate
    collections. Normal browser, API, and packaged-desktop launches do not set
    it and therefore always use ``~/streaks``.
    """
    selected = override if override is not None else os.getenv("STREAKS_DIR")
    return Path(selected).expanduser() if selected else default_streaks_dir()


# Backwards-compatible constant for the CLI and external callers.
DEFAULT_STREAKS_DIR = str(default_streaks_dir())

# Supported tick types
SUPPORTED_TICK_TYPES = ("Daily", "Weekly")

# Tick type to period mapping (in days)
TICK_PERIODS = {
    "Daily": 1,
    "Weekly": 7,
}
