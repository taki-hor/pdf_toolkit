"""
Optimize dialog for compressing and optimizing PDF files.
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
    select_pdf_file, select_save_file, format_file_size,
    show_success, show_error
)


class OptimizeDialog(tk.Frame):
    """
    Dialog for optimizing and compressing PDF files.
    """

    def __init__(self, parent, main_window):
        """
        Initialize optimize dialog.

        Args:
            parent: Parent widget
            main_window: Reference to main window
        """
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.input_file = None
        self.page_count = 0
        self.file_size = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Title
        title_label = tk.Label(
            self,
            text=f"{get_icon('optimize')} Optimize PDF",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Compress and optimize PDF file to reduce size",
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

        # Optimization settings
        optimize_frame = tk.LabelFrame(
            self,
            text="Optimization Settings",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        optimize_frame.pack(fill=tk.X, pady=SPACING["medium"])

        # Quality level
        quality_label = tk.Label(
            optimize_frame,
            text="Select optimization level:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor=tk.W
        )
        quality_label.pack(fill=tk.X, pady=(0, SPACING["small"]))

        self.quality_var = tk.StringVar(value="medium")

        # Quality options
        qualities = [
            ("low", "Low Quality", "Maximum compression (smallest file)"),
            ("medium", "Medium Quality", "Balanced compression and quality"),
            ("high", "High Quality", "Minimal compression (best quality)")
        ]

        for value, label, desc in qualities:
            rb_frame = tk.Frame(optimize_frame, bg=COLORS["bg_secondary"])
            rb_frame.pack(fill=tk.X, pady=SPACING["small"])

            rb = tk.Radiobutton(
                rb_frame,
                text=label,
                variable=self.quality_var,
                value=value,
                font=FONTS["default"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_primary"],
                selectcolor="white",
                activebackground=COLORS["bg_secondary"],
                activeforeground=COLORS["text_primary"]
            )
            rb.pack(side=tk.LEFT)

            desc_label = tk.Label(
                rb_frame,
                text=f" - {desc}",
                font=("Arial", 9),
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_secondary"]
            )
            desc_label.pack(side=tk.LEFT)

        # Optimization options
        ttk.Separator(optimize_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        options_label = tk.Label(
            optimize_frame,
            text="Additional options:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor=tk.W
        )
        options_label.pack(fill=tk.X, pady=(0, SPACING["small"]))

        # Remove unused objects
        self.remove_unused_var = tk.BooleanVar(value=True)
        remove_check = tk.Checkbutton(
            optimize_frame,
            text="Remove unused objects",
            variable=self.remove_unused_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"]
        )
        remove_check.pack(anchor=tk.W, pady=SPACING["small"])

        # Compress images
        self.compress_images_var = tk.BooleanVar(value=True)
        compress_check = tk.Checkbutton(
            optimize_frame,
            text="Compress images",
            variable=self.compress_images_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"]
        )
        compress_check.pack(anchor=tk.W, pady=SPACING["small"])

        # Remove duplicate streams
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        duplicates_check = tk.Checkbutton(
            optimize_frame,
            text="Remove duplicate streams",
            variable=self.remove_duplicates_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"]
        )
        duplicates_check.pack(anchor=tk.W, pady=SPACING["small"])

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
            text=f"{get_icon('rocket')} Optimize PDF",
            command=self._start_optimize,
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

        # Get page count and file size
        try:
            doc = fitz.open(filepath)
            self.page_count = doc.page_count
            doc.close()

            path = Path(filepath)
            self.file_size = path.stat().st_size

            self.file_info_label.config(
                text=f"{get_icon('success')} File loaded: {self.page_count} pages, {format_file_size(self.file_size)}",
                fg=COLORS["success"]
            )

            # Set default output
            if not self.output_entry.get():
                default_output = str(path.parent / f"{path.stem}_optimized.pdf")
                self.output_entry.insert(0, default_output)

            self._update_start_button()

        except Exception as e:
            show_error("Error", f"Cannot read PDF file:\n{str(e)}")
            self.input_file = None
            self.page_count = 0
            self.file_size = 0
            self.file_info_label.config(text="File read failed", fg=COLORS["error"])

    def _select_output_file(self) -> None:
        """Select output file."""
        default_name = self.output_entry.get() or "output_optimized.pdf"
        filepath = select_save_file(default_name=Path(default_name).name)
        if filepath:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filepath)
            self._update_start_button()

    def _update_start_button(self) -> None:
        """Update start button state."""
        has_input = self.input_file is not None
        has_output = len(self.output_entry.get().strip()) > 0
        self.start_btn.config(
            state=tk.NORMAL if (has_input and has_output) else tk.DISABLED
        )

    def _start_optimize(self) -> None:
        """Start optimize operation."""
        if not self.input_file:
            show_error("Error", "Please select a PDF file")
            return

        output = self.output_entry.get().strip()
        if not output:
            show_error("Error", "Please specify output file")
            return

        # Ensure .pdf extension
        if not output.lower().endswith('.pdf'):
            output += '.pdf'

        # Get optimization parameters
        quality = self.quality_var.get()
        remove_unused = self.remove_unused_var.get()
        compress_images = self.compress_images_var.get()
        remove_duplicates = self.remove_duplicates_var.get()

        quality_settings = {
            "low": {"target_reduction": 0.5, "dpi": 110},
            "medium": {"target_reduction": 0.3, "dpi": 150},
            "high": {"target_reduction": 0.15, "dpi": 220},
        }
        selected = quality_settings.get(quality, quality_settings["medium"])
        target_reduction = selected["target_reduction"]
        dpi = selected["dpi"]
        aggressive = quality == "low"
        linearize = quality == "high"

        # Show progress dialog
        progress = ProgressDialog(self, title="Optimize PDF")
        progress.update_status("Optimizing PDF file...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Optimization complete!")

            # Calculate size reduction
            if Path(output).exists():
                new_size = Path(output).stat().st_size
                reduction = ((self.file_size - new_size) / self.file_size) * 100

                self.main_window.show_message(
                    f"PDF optimized - {reduction:.1f}% size reduction",
                    "success"
                )
                show_success(
                    "Success",
                    f"PDF optimized successfully:\n{output}\n\n"
                    f"Original: {format_file_size(self.file_size)}\n"
                    f"Optimized: {format_file_size(new_size)}\n"
                    f"Reduction: {reduction:.1f}%"
                )
            else:
                self.main_window.show_message("PDF optimized successfully", "success")
                show_success("Success", f"PDF optimized successfully:\n{output}")

        def on_error(error):
            progress.error("Optimization failed")
            self.main_window.show_message("Optimization failed", "error")
            show_error("Error", f"Error optimizing PDF:\n{error}")

        worker = PDFWorker(
            operation="optimize",
            params={
                "input_pdf": self.input_file,
                "output_pdf": output,
                "quality": quality,
                "linearize": linearize,
                "aggressive": aggressive,
                "dpi": dpi,
                "remove_unused": remove_unused,
                "compress_images": compress_images,
                "remove_duplicates": remove_duplicates,
                "target_reduction": target_reduction
            },
            on_complete=on_complete,
            on_error=on_error
        )
        worker.start()

    def _reset(self) -> None:
        """Reset all fields."""
        self.input_file = None
        self.page_count = 0
        self.file_size = 0
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state="readonly")
        self.output_entry.delete(0, tk.END)
        self.quality_var.set("medium")
        self.remove_unused_var.set(True)
        self.compress_images_var.set(True)
        self.remove_duplicates_var.set(True)
        self.file_info_label.config(text="No file selected", fg=COLORS["text_secondary"])
        self._update_start_button()
        self.main_window.show_message("Reset", "info")
