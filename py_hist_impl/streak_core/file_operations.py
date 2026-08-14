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
File operations for the streak.txt format.
Handles loading and saving of streak files.
"""

import os
import re
import sys
from .constants import SUPPORTED_TICK_TYPES
from .models import Streak, DailyTick


class StreakFileManager:
    """
    Handles all file I/O operations for streak files.
    """

    @staticmethod
    def slugify_name(name):
        """Return the canonical filename-safe identifier for a streak name."""
        if not isinstance(name, str):
            raise ValueError("A streak name must be text")
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if not slug:
            raise ValueError("A streak name must contain letters or numbers")
        return slug

    @staticmethod
    def validate_metadata(metadata):
        """Ensure metadata can be represented safely in the line-based format."""
        for key, value in metadata.items():
            key_text = str(key)
            value_text = str(value)
            if not key_text or ":" in key_text or "\n" in key_text or "\r" in key_text:
                raise ValueError(f"Invalid metadata key: {key_text!r}")
            if "\n" in value_text or "\r" in value_text:
                raise ValueError(f"Metadata value for {key_text!r} must be a single line")

    @staticmethod
    def load_from_file(filepath):
        """
        Load a streak from a file.
        Returns a Streak object with all data populated.
        """
        streak = Streak()
        streak.streak_file = filepath
        
        # Read metadata and ticks
        StreakFileManager._read_metadata(streak)
        StreakFileManager._read_ticks(streak)
        
        # Calculate derived data
        streak.get_years()
        
        return streak

    @staticmethod
    def save_to_file(streak, filepath=None):
        """
        Save a streak to a file.
        If filepath is not provided, uses the streak's existing file path.
        """
        if filepath is None:
            filepath = getattr(streak, 'streak_file', None)
            if filepath is None:
                raise ValueError("No file path provided and streak has no existing file")        
        metadata = dict(streak.metadata)
        if streak.name:
            metadata["name"] = streak.name
        if streak.tick:
            metadata["tick"] = streak.tick
        StreakFileManager.validate_metadata(metadata)

        with open(filepath, "w") as f:
            # write the metadata
            f.write("---\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("---\n")
            for tick in streak.ticks:
                f.write(f"{tick.tick_datetime_str}\n")

        streak.metadata = metadata

    @staticmethod
    def _read_metadata(streak):
        """
        Read YAML front matter metadata from the streak file.
        """
        with open(streak.streak_file, "r") as f:
            line = f.readline()
            if line == "---\n":
                while True:
                    line = f.readline()
                    if line == "":
                        raise ValueError(f"Unterminated metadata block in {streak.streak_file}")
                    if line == "---\n":
                        break
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        key = key.strip()
                        value = value.strip()
                        streak.metadata[key] = value
        
        if "name" in streak.metadata:
            streak.name = streak.metadata["name"]
        if "tick" in streak.metadata:
            streak.tick = streak.metadata["tick"]
            # Set period based on tick type
            if streak.tick == "Daily":
                streak.period = 1
            elif streak.tick == "Weekly":
                streak.period = 7
            else:
                raise ValueError(f"Unsupported tick type: {streak.tick}")

    @staticmethod
    def _read_ticks(streak):
        """
        Read the ticks from the file.

        Supports both Daily and Weekly tick types.
        Each line after the metadata is a tick
        Each tick is in the date format ISO8601
        All of the ticks are stored in the ticks list
        """
        with open(streak.streak_file, "r") as f:
            # gobble up the yaml metadata if it exists
            line = f.readline()
            if line == "---\n":
                while True:
                    line = f.readline()
                    if line == "":
                        raise ValueError(f"Unterminated metadata block in {streak.streak_file}")
                    if line == "---\n":
                        break
                line = f.readline()
            # read the ticks, including the first line when no metadata exists
            while line:
                if line and line.strip():
                    streak.ticks.append(DailyTick(line.strip()))
                line = f.readline()

    @staticmethod
    def find_streak_file(directory, name):
        """
        Find a streak file by name in the given directory.
        Returns the full path to the file or None if not found.
        """
        if not os.path.exists(directory):
            return None
            
        files = os.listdir(directory)
        matches = [f for f in files if name.lower() in f.lower()]
        
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return os.path.join(directory, matches[0])
        else:
            # Multiple matches found
            raise ValueError(f"Multiple streaks found matching '{name}': {matches}")

    @staticmethod
    def get_streak_from_file_or_name(directory, file_path=None, name=None):
        """
        Get a streak either from a specific file path or by searching for a name.
        """
        if file_path:
            return StreakFileManager.load_from_file(file_path)
        elif name:
            found_file = StreakFileManager.find_streak_file(directory, name)
            if found_file is None:
                print("No streaks found")
                sys.exit(1)
            return StreakFileManager.load_from_file(found_file)
        else:
            print("No file or name provided")
            sys.exit(1)

    @staticmethod
    def create_new_streak_file(directory, name, tick_type="Daily", metadata=None):
        """
        Create a new streak file with the given name and tick type.
        Returns the path to the created file.
        """
        if tick_type not in SUPPORTED_TICK_TYPES:
            raise ValueError(f"tick_type must be one of: {', '.join(SUPPORTED_TICK_TYPES)}")

        normalized_name = name.strip() if isinstance(name, str) else name
        name_in_path = StreakFileManager.slugify_name(normalized_name)
        file_metadata = {"name": normalized_name, "tick": tick_type}
        if metadata:
            file_metadata.update(metadata)
        StreakFileManager.validate_metadata(file_metadata)

        os.makedirs(directory, exist_ok=True)
        streak_file = os.path.join(directory, f"streak-{name_in_path}.txt")

        try:
            with open(streak_file, "x") as f:
                f.write("---\n")
                for key, value in file_metadata.items():
                    f.write(f"{key}: {value}\n")
                f.write("---\n")
        except FileExistsError:
            raise FileExistsError(f"Streak file already exists: {streak_file}") from None
        
        return streak_file

    @staticmethod
    def list_streak_files(directory):
        """
        List all streak files in the given directory.
        Returns a list of file paths.
        """
        if not os.path.exists(directory):
            return []
            
        files = os.listdir(directory)
        streak_files = [f for f in files if f.startswith("streak-") and f.endswith(".txt")]
        return [os.path.join(directory, f) for f in streak_files]
