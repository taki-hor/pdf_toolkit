"""
Delete pages dialog for removing specific pages from PDF.
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
    select_pdf_file, select_save_file,
    show_success, show_error
)


class DeleteDialog(tk.Frame):
    """
    Dialog for deleting specific pages from PDF.
    """

    def __init__(self, parent, main_window):
        """
        Initialize delete dialog.

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
            text=f"{get_icon('delete')} Delete Pages",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Remove specific pages from PDF file",
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

        # Pages to delete
        delete_frame = tk.LabelFrame(
            self,
            text="Pages to Delete",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        delete_frame.pack(fill=tk.X, pady=SPACING["medium"])

        delete_input_frame = tk.Frame(delete_frame, bg=COLORS["bg_secondary"])
        delete_input_frame.pack(fill=tk.X)

        tk.Label(
            delete_input_frame,
            text="Page Numbers:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT)

        self.pages_entry = tk.Entry(
            delete_input_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            width=30
        )
        self.pages_entry.pack(side=tk.LEFT, padx=SPACING["small"])
        self.pages_entry.bind("<KeyRelease>", lambda _e: self._update_start_button())

        tk.Label(
            delete_input_frame,
            text="e.g., 1,3,5-7",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        ).pack(side=tk.LEFT)

        # Help text
        help_label = tk.Label(
            delete_frame,
            text="Enter page numbers to delete (comma-separated or ranges)",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            anchor=tk.W
        )
        help_label.pack(fill=tk.X, pady=(SPACING["small"], 0))

        # Output file
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
            text="Output File:",
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
        self.output_entry.bind("<KeyRelease>", lambda _e: self._update_start_button())

        browse_output_btn = tk.Button(
            output_select_frame,
            text=f"{get_icon('folder')} Browse",
            command=self._select_output_file,
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
            text=f"{get_icon('rocket')} Delete Pages",
            command=self._start_delete,
            bg=COLORS["error"],
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

            # Set default output
            if not self.output_entry.get():
                path = Path(filepath)
                default_output = str(path.parent / f"{path.stem}_deleted.pdf")
                self.output_entry.insert(0, default_output)

            self._update_start_button()

        except Exception as e:
            show_error("Error", f"Cannot read PDF file:\n{str(e)}")
            self.input_file = None
            self.page_count = 0
            self.file_info_label.config(text="File read failed", fg=COLORS["error"])

    def _select_output_file(self) -> None:
        """Select output file."""
        default_name = self.output_entry.get() or "output_deleted.pdf"
        filepath = select_save_file(default_name=Path(default_name).name)
        if filepath:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filepath)
            self._update_start_button()

    def _update_start_button(self) -> None:
        """Update start button state."""
        has_input = self.input_file is not None
        has_pages = len(self.pages_entry.get().strip()) > 0
        has_output = len(self.output_entry.get().strip()) > 0
        self.start_btn.config(
            state=tk.NORMAL if (has_input and has_pages and has_output) else tk.DISABLED
        )

    def _start_delete(self) -> None:
        """Start delete operation."""
        if not self.input_file:
            show_error("Error", "Please select a PDF file")
            return

        pages_str = self.pages_entry.get().strip()
        if not pages_str:
            show_error("Error", "Please enter page numbers to delete")
            return

        output = self.output_entry.get().strip()
        if not output:
            show_error("Error", "Please specify output file")
            return

        # Ensure .pdf extension
        if not output.lower().endswith('.pdf'):
            output += '.pdf'

        # Show progress dialog
        progress = ProgressDialog(self, title="Delete Pages")
        progress.update_status(f"Deleting pages from PDF...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Delete complete!")
            self.main_window.show_message("Pages deleted successfully", "success")
            show_success("Success", f"Pages deleted successfully:\n{output}")

        def on_error(error):
            progress.error("Delete failed")
            self.main_window.show_message("Delete failed", "error")
            show_error("Error", f"Error deleting pages:\n{error}")

        worker = PDFWorker(
            operation="delete",
            params={
                "input_pdf": self.input_file,
                "output_pdf": output,
                "page_spec": pages_str
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
        self.pages_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.file_info_label.config(text="No file selected", fg=COLORS["text_secondary"])
        self._update_start_button()
        self.main_window.show_message("Reset", "info")
