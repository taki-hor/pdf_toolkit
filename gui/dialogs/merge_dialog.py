"""
Merge PDF dialog for combining multiple PDF files.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from gui.widgets.file_list import FileListWidget
from gui.widgets.progress_dialog import ProgressDialog
from gui.workers.pdf_worker import PDFWorker
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import select_save_file, show_success, show_error


class MergeDialog(tk.Frame):
    """
    Dialog for merging multiple PDF files.
    """

    def __init__(self, parent, main_window):
        """
        Initialize merge dialog.

        Args:
            parent: Parent widget
            main_window: Reference to main window
        """
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.output_path = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Title
        title_label = tk.Label(
            self,
            text=f"{get_icon('merge')} Merge PDF",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Select PDF files to merge, files will be merged in list order",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=(0, SPACING["medium"]))

        # File list widget
        self.file_list = FileListWidget(
            self,
            on_files_changed=self._on_files_changed,
            allow_multiple=True,
            show_page_count=True
        )
        self.file_list.pack(fill=tk.BOTH, expand=True, pady=SPACING["medium"])

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        # Output settings
        output_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        output_frame.pack(fill=tk.X, pady=SPACING["medium"])

        output_label = tk.Label(
            output_frame,
            text="Output Settings:",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        output_label.pack(anchor=tk.W, pady=(0, SPACING["small"]))

        # Output file selection
        output_select_frame = tk.Frame(output_frame, bg=COLORS["bg_secondary"])
        output_select_frame.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            output_select_frame,
            text="Output File:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=10,
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
        self.output_entry.insert(0, "merged_output.pdf")

        browse_btn = tk.Button(
            output_select_frame,
            text=f"{get_icon('folder')} Browse",
            command=self._browse_output,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT)

        # Options
        self.open_after_var = tk.BooleanVar(value=False)
        open_check = tk.Checkbutton(
            output_frame,
            text="Open file when complete",
            variable=self.open_after_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"]
        )
        open_check.pack(anchor=tk.W, pady=SPACING["small"])

        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X, pady=SPACING["large"])

        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text=f"{get_icon('rocket')} Start Merge",
            command=self._start_merge,
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

    def _browse_output(self) -> None:
        """Open save file dialog."""
        default_name = self.output_entry.get() or "merged_output.pdf"
        filepath = select_save_file(default_name=default_name)
        if filepath:
            self.output_path = filepath
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filepath)

    def _on_files_changed(self, files: list) -> None:
        """
        Handle file list changes.

        Args:
            files: List of file paths
        """
        # Enable/disable start button
        has_files = len(files) >= 2
        self.start_btn.config(
            state=tk.NORMAL if has_files else tk.DISABLED
        )

        # Update main window status
        if has_files:
            self.main_window.show_message(
                f"Selected {len(files)} files, ready to merge",
                "info"
            )
        else:
            self.main_window.show_message(
                "Please select at least 2 PDF files",
                "warning"
            )

    def _start_merge(self) -> None:
        """Start merge operation."""
        files = self.file_list.get_files()
        if len(files) < 2:
            show_error("Error", "Please select at least 2 PDF files")
            return

        output = self.output_entry.get().strip()
        if not output:
            show_error("Error", "Please specify output file name")
            return

        # Ensure .pdf extension
        if not output.lower().endswith('.pdf'):
            output += '.pdf'

        # Show progress dialog
        progress = ProgressDialog(self, title="Merge PDF")
        progress.update_status(f"Merging {len(files)} files...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Merge complete!")
            self.main_window.show_message(f"Successfully merged {len(files)} files", "success")
            show_success("Success", f"PDF successfully merged to:\n{output}")

            # Open file if requested
            if self.open_after_var.get():
                import os
                import platform
                if platform.system() == "Windows":
                    os.startfile(output)
                elif platform.system() == "Darwin":
                    os.system(f"open '{output}'")
                else:
                    os.system(f"xdg-open '{output}'")

        def on_error(error):
            progress.error("Merge failed")
            self.main_window.show_message("Merge failed", "error")
            show_error("Error", f"Error merging PDF:\n{error}")

        worker = PDFWorker(
            operation="merge",
            params={
                "input_pdfs": files,
                "output_pdf": output
            },
            on_complete=on_complete,
            on_error=on_error
        )
        worker.start()

    def _reset(self) -> None:
        """Reset all fields."""
        self.file_list.clear()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, "merged_output.pdf")
        self.open_after_var.set(False)
        self.main_window.show_message("Reset", "info")
