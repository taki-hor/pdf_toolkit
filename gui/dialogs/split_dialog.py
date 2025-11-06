"""
Split PDF dialog for dividing PDF into multiple files.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import fitz  # PyMuPDF

from gui.widgets.progress_dialog import ProgressDialog
from gui.workers.pdf_worker import PDFWorker
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import (
    select_pdf_file, select_directory,
    show_success, show_error, show_warning
)


class SplitDialog(tk.Frame):
    """
    Dialog for splitting PDF into multiple files.
    """

    def __init__(self, parent, main_window):
        """
        Initialize split dialog.

        Args:
            parent: Parent widget
            main_window: Reference to main window
        """
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.input_file = None
        self.page_count = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Title
        title_label = tk.Label(
            self,
            text=f"{get_icon('split')} Split PDF",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Select PDF file and set split mode",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=(0, SPACING["medium"]))

        # Input file selection
        input_frame = tk.LabelFrame(
            self,
            text="Source File",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        input_frame.pack(fill=tk.X, pady=SPACING["medium"])

        input_select_frame = tk.Frame(input_frame, bg=COLORS["bg_secondary"])
        input_select_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(
            input_select_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            state="readonly"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        browse_btn = tk.Button(
            input_select_frame,
            text=f"{get_icon('folder')} Select File",
            command=self._select_input_file,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT)

        # File info label
        self.file_info_label = tk.Label(
            input_frame,
            text="No file selected",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            anchor=tk.W
        )
        self.file_info_label.pack(fill=tk.X, pady=(SPACING["small"], 0))

        # Split mode selection
        mode_frame = tk.LabelFrame(
            self,
            text="Split Mode",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        mode_frame.pack(fill=tk.X, pady=SPACING["medium"])

        self.split_mode = tk.StringVar(value="all")

        # Mode: Split all pages
        all_radio = tk.Radiobutton(
            mode_frame,
            text="Split into single page files (one PDF per page)",
            variable=self.split_mode,
            value="all",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_mode_change
        )
        all_radio.pack(anchor=tk.W, pady=SPACING["small"])

        # Mode: Split by range
        range_radio = tk.Radiobutton(
            mode_frame,
            text="Split by page range",
            variable=self.split_mode,
            value="range",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_mode_change
        )
        range_radio.pack(anchor=tk.W, pady=SPACING["small"])

        # Range input (initially disabled)
        range_input_frame = tk.Frame(mode_frame, bg=COLORS["bg_secondary"])
        range_input_frame.pack(fill=tk.X, padx=(30, 0), pady=SPACING["small"])

        tk.Label(
            range_input_frame,
            text="Page Range:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT)

        self.range_entry = tk.Entry(
            range_input_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            state=tk.DISABLED,
            width=30
        )
        self.range_entry.pack(side=tk.LEFT, padx=SPACING["small"])

        tk.Label(
            range_input_frame,
            text="e.g., 1-3,5,7-9",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        ).pack(side=tk.LEFT)

        # Output directory
        output_frame = tk.LabelFrame(
            self,
            text="Output Settings",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        output_frame.pack(fill=tk.X, pady=SPACING["medium"])

        output_select_frame = tk.Frame(output_frame, bg=COLORS["bg_secondary"])
        output_select_frame.pack(fill=tk.X)

        tk.Label(
            output_select_frame,
            text="Output Folder:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.output_entry = tk.Entry(
            output_select_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["small"])

        browse_output_btn = tk.Button(
            output_select_frame,
            text=f"{get_icon('folder')} Browse",
            command=self._select_output_dir,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        browse_output_btn.pack(side=tk.LEFT)

        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X, pady=SPACING["large"])

        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text=f"{get_icon('rocket')} Start Split",
            command=self._start_split,
            bg=COLORS["accent"],
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.RIGHT, padx=SPACING["small"])

        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text=f"{get_icon('refresh')} Reset",
            command=self._reset,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.RIGHT, padx=SPACING["small"])

    def _select_input_file(self) -> None:
        """Select input PDF file."""
        filepath = select_pdf_file()
        if not filepath:
            return

        self.input_file = filepath
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filepath)
        self.input_entry.config(state="readonly")

        # Get page count
        try:
            doc = fitz.open(filepath)
            self.page_count = doc.page_count
            doc.close()

            self.file_info_label.config(
                text=f"{get_icon('success')} File loaded: {self.page_count} pages",
                fg=COLORS["success"]
            )

            # Set default output directory
            if not self.output_entry.get():
                default_dir = str(Path(filepath).parent / "split_output")
                self.output_entry.insert(0, default_dir)

            self._update_start_button()

        except Exception as e:
            show_error("Error", f"Cannot read PDF file:\n{str(e)}")
            self.input_file = None
            self.page_count = 0
            self.file_info_label.config(text="File read failed", fg=COLORS["error"])

    def _select_output_dir(self) -> None:
        """Select output directory."""
        directory = select_directory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            self._update_start_button()

    def _on_mode_change(self) -> None:
        """Handle split mode change."""
        mode = self.split_mode.get()
        if mode == "range":
            self.range_entry.config(state=tk.NORMAL)
        else:
            self.range_entry.config(state=tk.DISABLED)

    def _update_start_button(self) -> None:
        """Update start button state."""
        has_input = self.input_file is not None
        has_output = len(self.output_entry.get().strip()) > 0
        self.start_btn.config(
            state=tk.NORMAL if (has_input and has_output) else tk.DISABLED
        )

    def _start_split(self) -> None:
        """Start split operation."""
        if not self.input_file:
            show_error("Error", "Please select a PDF file to split")
            return

        output_dir = self.output_entry.get().strip()
        if not output_dir:
            show_error("Error", "Please specify output folder")
            return

        # Get page spec based on mode
        page_spec = None
        if self.split_mode.get() == "range":
            page_spec = self.range_entry.get().strip()
            if not page_spec:
                show_error("Error", "Please enter page range")
                return

        # Show progress dialog
        progress = ProgressDialog(self, title="Split PDF")
        progress.update_status("Splitting PDF...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Split complete!")
            self.main_window.show_message("Split complete", "success")
            show_success("Success", f"PDF successfully split to folder:\n{output_dir}")

        def on_error(error):
            progress.error("Split failed")
            self.main_window.show_message("Split failed", "error")
            show_error("Error", f"Error splitting PDF:\n{error}")

        worker = PDFWorker(
            operation="split",
            params={
                "input_pdf": self.input_file,
                "output_dir": output_dir,
                "page_spec": page_spec
            },
            on_complete=on_complete,
            on_error=on_error
        )
        worker.start()

    def _reset(self) -> None:
        """Reset all fields."""
        self.input_file = None
        self.page_count = 0
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state="readonly")
        self.output_entry.delete(0, tk.END)
        self.range_entry.delete(0, tk.END)
        self.split_mode.set("all")
        self.range_entry.config(state=tk.DISABLED)
        self.file_info_label.config(text="No file selected", fg=COLORS["text_secondary"])
        self._update_start_button()
        self.main_window.show_message("Reset", "info")
