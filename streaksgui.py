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
streaksgui.py - Tkinter GUI for the streak.txt format.
A simple GUI to quickly mark daily streaks.

author: Abhishek Mishra
date: 18/06/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
from streak_core import (
    Streak,
    StreakFileManager,
    StreakStatsCalculator,
    DEFAULT_STREAKS_DIR,
)


# Add constants for UI settings
class UIConstants:
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500
    DIALOG_WIDTH = 400
    DIALOG_HEIGHT = 300

    # Fonts
    TITLE_FONT = ("Arial", 18, "bold")
    SUBTITLE_FONT = ("Arial", 14)
    BODY_FONT = ("Arial", 12)
    SMALL_FONT = ("Arial", 10)

    # Colors
    SUCCESS_COLOR = "#405240"  # Grayish green
    PRIMARY_COLOR = "#4A6B8A"  # Lighter grayish blue
    APP_BG = "#000000"  # Black
    TEXT_GRAY = "#808080"  # Gray
    TEXT_FG = "#00FF00"  # Green
    BORDER_FG = "#31E231"  # Light green border color

    # Padding
    MAIN_PADDING = 20
    WIDGET_PADDING = 10
    SMALL_PADDING = 5


class GUIStreak(Streak):
    """
    GUI-compatible Streak class that includes file path and auto-save functionality.
    """

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path

        if file_path:
            # Load from file
            loaded_streak = StreakFileManager.load_from_file(file_path)
            self.name = loaded_streak.name
            self.tick = loaded_streak.tick
            self.metadata = loaded_streak.metadata
            self.ticks = loaded_streak.ticks
            self.period = loaded_streak.period

            # Calculate statistics
            StreakStatsCalculator.calculate_stats(self)

    def mark_today(self):
        """Mark today and save to file automatically"""
        result = super().mark_today()
        if result and self.file_path:
            StreakFileManager.save_to_file(self, self.file_path)
            # Recalculate stats
            StreakStatsCalculator.calculate_stats(self)
        return result


class QuickTickDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Streak Quick Tick")
        self.root.geometry(f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}")
        
        # Configure window theme
        self.root.configure(bg=UIConstants.APP_BG)

        # Directory setup
        self.streaks_dir = DEFAULT_STREAKS_DIR
        self.streaks = []

        self.setup_ui()
        self.load_streaks()

    def _bind_mousewheel(self, widget):
        def _on_mousewheel(event):
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        widget.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))  # Linux scroll up
        widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))   # Linux scroll down

    def setup_ui(self):        # Title
        title_label = tk.Label(
            self.root, text="Today's Streaks", font=UIConstants.TITLE_FONT,
            bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG
        )
        title_label.pack(pady=UIConstants.MAIN_PADDING)

        # Date display
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        date_label = tk.Label(self.root, text=today, font=UIConstants.SUBTITLE_FONT,
                             bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG)
        date_label.pack(pady=UIConstants.SMALL_PADDING)        # Main content frame
        content_frame = tk.Frame(self.root, bg=UIConstants.APP_BG)
        content_frame.pack(
            fill="both",
            expand=True,
            padx=UIConstants.MAIN_PADDING,
            pady=UIConstants.WIDGET_PADDING,
        )

        # Scrollable frame for streaks
        canvas = tk.Canvas(content_frame, bg=UIConstants.APP_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            content_frame, orient="vertical", command=canvas.yview
        )
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self._bind_mousewheel(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")        # Bottom frame
        bottom_frame = tk.Frame(self.root, bg=UIConstants.APP_BG)
        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=UIConstants.MAIN_PADDING,
            pady=UIConstants.WIDGET_PADDING,
        )

        # Buttons frame
        button_frame = tk.Frame(bottom_frame, bg=UIConstants.APP_BG)
        button_frame.pack(side="top", fill="x", pady=(0, UIConstants.SMALL_PADDING))        # Create Refresh button using utility function
        refresh_frame, refresh_btn = UIHelper.create_bordered_button(
            parent=button_frame,
            text="🔄 Refresh",
            command=self.refresh_streaks
        )
        refresh_frame.pack(side="left", padx=2, pady=2)

        # Create New Streak button using utility function
        new_streak_frame, new_streak_btn = UIHelper.create_bordered_button(
            parent=button_frame,
            text="➕ New Streak",
            command=self.create_new_streak
        )
        new_streak_frame.pack(side="left", padx=(UIConstants.SMALL_PADDING + 2, 2), pady=2)

        # Summary label
        self.summary_label = tk.Label(
            bottom_frame, text="", font=UIConstants.SUBTITLE_FONT,
            bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG
        )
        self.summary_label.pack()

    def load_streaks(self):
        """Load all streak files from the directory"""
        if not os.path.exists(self.streaks_dir):
            os.makedirs(self.streaks_dir)

        self.streaks = []
        try:
            streak_files = StreakFileManager.list_streak_files(self.streaks_dir)

            for streak_file in streak_files:
                try:
                    streak = GUIStreak(streak_file)
                    self.streaks.append(streak)
                except Exception as e:
                    print(f"Error loading {streak_file}: {e}")
        except Exception as e:
            print(f"Error accessing streaks directory: {e}")

        self.display_streaks()

    def display_streaks(self):
        """Display all streaks with tick buttons"""
        self._clear_existing_widgets()

        if not self.streaks:
            self._show_no_streaks_message()
            return

        ticked_count = self._display_streak_items()
        self._update_summary(ticked_count)

    def _clear_existing_widgets(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _show_no_streaks_message(self):
        no_streaks_label = tk.Label(
            self.scrollable_frame,            text="No streaks found. Click 'New Streak' to create one!",
            font=UIConstants.SUBTITLE_FONT,
            fg=UIConstants.TEXT_GRAY,
            bg=UIConstants.APP_BG,
        )
        no_streaks_label.pack(pady=UIConstants.SMALL_PADDING)
        self.summary_label.config(text="No streaks to display")

    def _display_streak_items(self):
        today = datetime.datetime.now().date()
        ticked_count = 0

        for streak in self.streaks:
            already_ticked = self._is_streak_ticked_today(streak, today)
            if already_ticked:
                ticked_count += 1

            self._create_streak_widget(streak, already_ticked)

        return ticked_count

    def _is_streak_ticked_today(self, streak, today):
        return any(tick.get_date() == today for tick in streak.ticks)

    def _create_streak_widget(self, streak, already_ticked):
        streak_frame = tk.Frame(
            self.scrollable_frame,
            relief="solid",
            borderwidth=1,
            bg=UIConstants.APP_BG,
        )
        streak_frame.pack(
            fill="x", padx=UIConstants.SMALL_PADDING, pady=UIConstants.SMALL_PADDING
        )

        main_frame = tk.Frame(streak_frame, bg=UIConstants.APP_BG)
        main_frame.pack(
            fill="x", padx=UIConstants.SMALL_PADDING, pady=UIConstants.SMALL_PADDING
        )

        info_frame = tk.Frame(main_frame, bg=UIConstants.APP_BG)
        info_frame.pack(side="left", fill="x", expand=True)

        name_label = tk.Label(
            info_frame,
            text=streak.name,
            font=UIConstants.BODY_FONT,
            bg=UIConstants.APP_BG,
            fg=UIConstants.TEXT_FG,
        )
        name_label.pack(anchor="w")

        type_label = tk.Label(
            info_frame,
            text=f"Type: {streak.tick}",
            font=UIConstants.SMALL_FONT,
            fg=UIConstants.TEXT_GRAY,
            bg=UIConstants.APP_BG,
        )
        type_label.pack(anchor="w")

        stats = streak.stats
        stats_text = f"Current: {stats['current_streak']} | Longest: {stats['longest_streak']} | Success: {stats['tick_average']*100:.0f}%"
        stats_label = tk.Label(
            info_frame,
            text=stats_text,
            font=UIConstants.BODY_FONT,
            fg=UIConstants.TEXT_GRAY,
            bg=UIConstants.APP_BG,
        )
        stats_label.pack(anchor="w", pady=(UIConstants.SMALL_PADDING, 0))

        button_frame = tk.Frame(main_frame, bg=UIConstants.APP_BG)
        button_frame.pack(side="right", padx=UIConstants.MAIN_PADDING)

        if already_ticked:
            tick_btn = tk.Button(
                button_frame,
                text="✓ Done Today",
                bg=UIConstants.SUCCESS_COLOR,
                fg=UIConstants.TEXT_FG,
                activebackground=UIConstants.SUCCESS_COLOR,
                activeforeground=UIConstants.TEXT_FG,
                state="disabled",
                width=12,
                height=2,
                font=UIConstants.BODY_FONT,
                highlightbackground=UIConstants.BORDER_FG,
                highlightcolor=UIConstants.BORDER_FG,
                highlightthickness=1,
                relief="solid",
                bd=1,
                disabledforeground=UIConstants.TEXT_FG,
            )
        else:
            tick_btn = tk.Button(
                button_frame,
                text="Mark Done",
                bg=UIConstants.PRIMARY_COLOR,
                fg=UIConstants.TEXT_FG,
                activebackground=UIConstants.PRIMARY_COLOR,
                activeforeground=UIConstants.TEXT_FG,
                width=12,
                height=2,
                font=UIConstants.BODY_FONT,
                command=lambda s=streak: self.tick_streak(s),
                highlightbackground=UIConstants.BORDER_FG,
                highlightcolor=UIConstants.BORDER_FG,
                highlightthickness=1,
                relief="solid",
                bd=1,
                overrelief="solid",
                default="normal",
            )
            # Force the button to use our colors
            tick_btn.config(bg=UIConstants.PRIMARY_COLOR)

        tick_btn.pack()

    def _update_summary(self, ticked_count):
        total_streaks = len(self.streaks)
        completion_rate = (
            (ticked_count / total_streaks * 100) if total_streaks > 0 else 0
        )
        self.summary_label.config(
            text=f"Today's Progress: {ticked_count}/{total_streaks} ({completion_rate:.0f}%)"
        )

    def tick_streak(self, streak):
        """Mark a streak as ticked for today"""
        try:
            streak.mark_today()
            self.display_streaks()  # Refresh the display
            messagebox.showinfo("Success", f"✓ Marked '{streak.name}' for today!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to tick '{streak.name}': {str(e)}")

    def refresh_streaks(self):
        """Reload streaks from disk"""
        self.load_streaks()

    def create_new_streak(self):
        """Open dialog to create a new streak"""
        dialog = NewStreakDialog(self.root, self.streaks_dir)
        if dialog.result:
            self.refresh_streaks()

    def run(self):
        self.root.mainloop()


class NewStreakDialog:
    def __init__(self, parent, streaks_dir):
        self.parent = parent
        self.streaks_dir = streaks_dir
        self.result = None        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Streak")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure dialog theme
        self.dialog.configure(bg=UIConstants.APP_BG)

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")

        self.setup_dialog()

    def setup_dialog(self):
        # Title
        title_label = tk.Label(
            self.dialog, text="Create New Streak", font=("Arial", 16, "bold"),
            bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG
        )
        title_label.pack(pady=20)

        # Name input
        name_frame = tk.Frame(self.dialog, bg=UIConstants.APP_BG)
        name_frame.pack(pady=10, padx=30, fill="x")

        tk.Label(name_frame, text="Streak Name:", font=("Arial", 12),
                bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG).pack(anchor="w")
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12),
                                  bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG,
                                  insertbackground=UIConstants.TEXT_FG)
        self.name_entry.pack(fill="x", pady=(5, 0))
        self.name_entry.focus()

        # Tick type selection
        tick_frame = tk.Frame(self.dialog, bg=UIConstants.APP_BG)
        tick_frame.pack(pady=10, padx=30, fill="x")

        tk.Label(tick_frame, text="Tick Type:", font=("Arial", 12),
                bg=UIConstants.APP_BG, fg=UIConstants.TEXT_FG).pack(anchor="w")
        self.tick_var = tk.StringVar(value="Daily")
        tick_combo = ttk.Combobox(
            tick_frame,
            textvariable=self.tick_var,
            values=["Daily", "Weekly"],
            state="readonly",
            font=("Arial", 12),
        )
        tick_combo.pack(fill="x", pady=(5, 0))        # Buttons
        button_frame = tk.Frame(self.dialog, bg=UIConstants.APP_BG)
        button_frame.pack(pady=30)

        create_btn = tk.Button(
            button_frame,
            text="Create Streak",
            command=self.create_streak,
            bg="#4CAF50",
            fg="#FFFFFF",
            activebackground="#4CAF50",
            activeforeground="#FFFFFF",
            font=("Arial", 12, "bold"),
            width=12,
            highlightbackground=UIConstants.BORDER_FG,
            highlightcolor=UIConstants.BORDER_FG,
            highlightthickness=1,
            relief="solid",
            bd=1,
        )
        create_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Arial", 12),
            width=12,
            bg=UIConstants.APP_BG,
            fg=UIConstants.TEXT_FG,
            activebackground=UIConstants.APP_BG,
            activeforeground=UIConstants.TEXT_FG,
            highlightbackground=UIConstants.BORDER_FG,
            highlightcolor=UIConstants.BORDER_FG,
            highlightthickness=1,
            relief="solid",
            bd=1,
        )
        cancel_btn.pack(side="left", padx=5)  # Bind Enter key to create
        self.dialog.bind("<Return>", lambda e: self.create_streak())

    def create_streak(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a streak name")
            return

        tick_type = self.tick_var.get()

        try:
            # Use the StreakFileManager to create the streak file
            filepath = StreakFileManager.create_new_streak_file(
                self.streaks_dir, name, tick_type
            )

            self.result = True
            messagebox.showinfo("Success", f"Created new streak: '{name}'")
            self.dialog.destroy()

        except FileExistsError:
            messagebox.showerror("Error", f"A streak with name '{name}' already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create streak: {str(e)}")


class UIHelper:
    """
    Utility class for creating consistent UI elements with proper theming.
    
    This class provides static methods for creating UI components that follow
    the application's dark theme with green borders and text.
    """
    
    @staticmethod
    def create_bordered_button(parent, text, command=None, font=None, 
                              bg_color=None, fg_color=None, border_color=None,
                              width=None, height=None, padx=2, pady=2):
        """
        Create a button with a visible colored border using a frame wrapper.
        
        This method creates a button with a clearly visible border by wrapping
        the button in a colored frame. This approach ensures the border is
        always visible regardless of platform or focus state.
        
        Args:
            parent (tk.Widget): The parent widget to contain the button
            text (str): The text to display on the button
            command (callable, optional): The function to call when button is clicked
            font (tuple, optional): Font specification (family, size, style). 
                                  Defaults to UIConstants.BODY_FONT
            bg_color (str, optional): Background color hex code. 
                                    Defaults to UIConstants.APP_BG
            fg_color (str, optional): Text color hex code. 
                                    Defaults to UIConstants.TEXT_FG
            border_color (str, optional): Border color hex code. 
                                        Defaults to UIConstants.BORDER_FG
            width (int, optional): Button width in characters
            height (int, optional): Button height in text lines
            padx (int): Horizontal padding around the border frame (default: 2)
            pady (int): Vertical padding around the border frame (default: 2)
            
        Returns:
            tuple: (border_frame, button) - The border frame and button widgets
            
        Example:
            # Create a basic bordered button
            frame, btn = UIHelper.create_bordered_button(
                parent=button_container,
                text="Click Me",
                command=my_function
            )
            frame.pack(side="left", padx=5)
            
            # Create a custom styled button
            frame, btn = UIHelper.create_bordered_button(
                parent=button_container,
                text="Custom Button",
                command=my_function,
                width=15,
                height=2,
                border_color="#FF0000"  # Red border
            )
            frame.pack(side="left", padx=10)
        """
        # Set default values from UIConstants if not provided
        if font is None:
            font = UIConstants.BODY_FONT
        if bg_color is None:
            bg_color = UIConstants.APP_BG
        if fg_color is None:
            fg_color = UIConstants.TEXT_FG
        if border_color is None:
            border_color = UIConstants.BORDER_FG
            
        # Create the border frame with colored background
        border_frame = tk.Frame(
            parent,
            bg=border_color,
            bd=2,
            relief="solid"
        )
        
        # Create the button inside the border frame
        button_kwargs = {
            'text': text,
            'font': font,
            'bg': bg_color,
            'fg': fg_color,
            'activebackground': bg_color,
            'activeforeground': fg_color,
            'relief': 'flat',
            'bd': 0
        }
        
        # Add optional parameters if provided
        if command is not None:
            button_kwargs['command'] = command
        if width is not None:
            button_kwargs['width'] = width
        if height is not None:
            button_kwargs['height'] = height
            
        button = tk.Button(border_frame, **button_kwargs)
        
        # Pack the button with small padding to show the border
        button.pack(padx=1, pady=1)
        
        return border_frame, button


if __name__ == "__main__":
    app = QuickTickDashboard()
    app.run()
