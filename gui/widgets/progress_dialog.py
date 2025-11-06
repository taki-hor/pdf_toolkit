"""
Progress dialog widget for PDF operations.
"""

import tkinter as tk
from tkinter import ttk
from gui.utils.theme import COLORS, FONTS
from gui.utils.helpers import center_window


class ProgressDialog(tk.Toplevel):
    """
    Modal dialog showing progress for PDF operations.
    """

    def __init__(self, parent, title: str = "Processing", cancelable: bool = False):
        """
        Initialize progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
            cancelable: Whether to show cancel button
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("450x180")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.cancelable = cancelable
        self.cancelled = False

        self._setup_ui()
        center_window(self, 450, 180)

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Main container
        container = tk.Frame(self, bg=COLORS["bg_secondary"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status label
        self.status_label = tk.Label(
            container,
            text="Processing...",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        self.status_label.pack(pady=(0, 15))

        # Progress bar
        self.progress = ttk.Progressbar(
            container,
            mode="indeterminate",
            length=400
        )
        self.progress.pack(pady=10)
        self.progress.start(10)

        # Detail label (optional, hidden by default)
        self.detail_label = tk.Label(
            container,
            text="",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        self.detail_label.pack(pady=(5, 10))

        # Cancel button (if cancelable)
        if self.cancelable:
            cancel_btn = tk.Button(
                container,
                text="Cancel",
                command=self.cancel,
                bg=COLORS["border"],
                fg=COLORS["text_primary"],
                font=FONTS["button"],
                padx=20,
                pady=5,
                relief=tk.FLAT,
                cursor="hand2"
            )
            cancel_btn.pack(pady=10)

    def update_status(self, text: str, detail: str = "") -> None:
        """
        Update progress status.

        Args:
            text: Main status text
            detail: Optional detail text
        """
        self.status_label.config(text=text)
        if detail:
            self.detail_label.config(text=detail)
        self.update()

    def set_progress(self, percent: float) -> None:
        """
        Set determinate progress.

        Args:
            percent: Progress percentage (0-100)
        """
        self.progress.config(mode="determinate")
        self.progress["value"] = percent
        self.update()

    def cancel(self) -> None:
        """Handle cancel button click."""
        self.cancelled = True
        self.destroy()

    def complete(self, message: str = "Complete!") -> None:
        """
        Mark operation as complete and close dialog.

        Args:
            message: Completion message
        """
        self.update_status(message)
        self.progress.stop()
        self.progress.config(mode="determinate", value=100)
        self.after(800, self.destroy)

    def error(self, message: str = "Error occurred") -> None:
        """
        Mark operation as failed.

        Args:
            message: Error message
        """
        self.update_status(message)
        self.progress.stop()
        self.status_label.config(fg=COLORS["error"])
        if not self.cancelable:
            # Add close button if not cancelable
            close_btn = tk.Button(
                self.winfo_children()[0],
                text="Close",
                command=self.destroy,
                bg=COLORS["error"],
                fg="white",
                font=FONTS["button"],
                padx=20,
                pady=5,
                relief=tk.FLAT,
                cursor="hand2"
            )
            close_btn.pack(pady=10)
