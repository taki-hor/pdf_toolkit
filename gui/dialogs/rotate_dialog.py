"""
Rotate pages dialog for changing page orientation.
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


class RotateDialog(tk.Frame):
    """
    Dialog for rotating PDF pages.
    """

    def __init__(self, parent, main_window):
        """
        Initialize rotate dialog.

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
            text=f"{get_icon('rotate')} Rotate Pages",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Rotate pages by 90, 180, or 270 degrees",
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

        # Rotation settings
        rotation_frame = tk.LabelFrame(
            self,
            text="Rotation Settings",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        rotation_frame.pack(fill=tk.X, pady=SPACING["medium"])

        # Page selection mode
        mode_label = tk.Label(
            rotation_frame,
            text="Select pages to rotate:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor=tk.W
        )
        mode_label.pack(fill=tk.X, pady=(0, SPACING["small"]))

        self.page_mode = tk.StringVar(value="all")

        # All pages option
        all_radio = tk.Radiobutton(
            rotation_frame,
            text="All pages",
            variable=self.page_mode,
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

        # Specific pages option
        specific_radio = tk.Radiobutton(
            rotation_frame,
            text="Specific pages",
            variable=self.page_mode,
            value="specific",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_mode_change
        )
        specific_radio.pack(anchor=tk.W, pady=SPACING["small"])

        # Page range input
        pages_input_frame = tk.Frame(rotation_frame, bg=COLORS["bg_secondary"])
        pages_input_frame.pack(fill=tk.X, padx=(30, 0), pady=SPACING["small"])

        tk.Label(
            pages_input_frame,
            text="Pages:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        ).pack(side=tk.LEFT)

        self.pages_entry = tk.Entry(
            pages_input_frame,
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
        self.pages_entry.pack(side=tk.LEFT, padx=SPACING["small"])
        self.pages_entry.bind("<KeyRelease>", lambda _e: self._update_start_button())

        tk.Label(
            pages_input_frame,
            text="e.g., 1-3,5,7-9",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        ).pack(side=tk.LEFT)

        # Rotation angle
        ttk.Separator(rotation_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        angle_label = tk.Label(
            rotation_frame,
            text="Rotation angle:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            anchor=tk.W
        )
        angle_label.pack(fill=tk.X, pady=(0, SPACING["small"]))

        self.angle_var = tk.StringVar(value="90")

        angle_options_frame = tk.Frame(rotation_frame, bg=COLORS["bg_secondary"])
        angle_options_frame.pack(fill=tk.X, pady=SPACING["small"])

        for angle in ["90", "180", "270"]:
            rb = tk.Radiobutton(
                angle_options_frame,
                text=f"{angle} deg clockwise",
                variable=self.angle_var,
                value=angle,
                font=FONTS["default"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_primary"],
                selectcolor="white",
                activebackground=COLORS["bg_secondary"],
                activeforeground=COLORS["text_primary"]
            )
            rb.pack(side=tk.LEFT, padx=(0, SPACING["large"]))

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
            text=f"{get_icon('rocket')} Rotate Pages",
            command=self._start_rotate,
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

            # Set default output
            if not self.output_entry.get():
                path = Path(filepath)
                default_output = str(path.parent / f"{path.stem}_rotated.pdf")
                self.output_entry.insert(0, default_output)

            self._update_start_button()

        except Exception as e:
            show_error("Error", f"Cannot read PDF file:\n{str(e)}")
            self.input_file = None
            self.page_count = 0
            self.file_info_label.config(text="File read failed", fg=COLORS["error"])

    def _select_output_file(self) -> None:
        """Select output file."""
        default_name = self.output_entry.get() or "output_rotated.pdf"
        filepath = select_save_file(default_name=Path(default_name).name)
        if filepath:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filepath)
            self._update_start_button()

    def _on_mode_change(self) -> None:
        """Handle page mode change."""
        mode = self.page_mode.get()
        if mode == "specific":
            self.pages_entry.config(state=tk.NORMAL)
        else:
            self.pages_entry.config(state=tk.NORMAL)
            self.pages_entry.delete(0, tk.END)
            self.pages_entry.config(state=tk.DISABLED)
        self._update_start_button()

    def _update_start_button(self) -> None:
        """Update start button state."""
        has_input = self.input_file is not None
        has_output = len(self.output_entry.get().strip()) > 0
        has_pages = True
        if self.page_mode.get() == "specific":
            has_pages = len(self.pages_entry.get().strip()) > 0
        self.start_btn.config(
            state=tk.NORMAL if (has_input and has_output and has_pages) else tk.DISABLED
        )

    def _start_rotate(self) -> None:
        """Start rotate operation."""
        if not self.input_file:
            show_error("Error", "Please select a PDF file")
            return

        output = self.output_entry.get().strip()
        if not output:
            show_error("Error", "Please specify output file")
            return

        # Get pages
        page_spec = None
        if self.page_mode.get() == "specific":
            page_spec = self.pages_entry.get().strip()
            if not page_spec:
                show_error("Error", "Please enter page numbers")
                return

        # Get angle
        angle = int(self.angle_var.get())

        # Ensure .pdf extension
        if not output.lower().endswith('.pdf'):
            output += '.pdf'

        # Show progress dialog
        progress = ProgressDialog(self, title="Rotate Pages")
        progress.update_status(f"Rotating pages by {angle} degrees...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Rotation complete!")
            self.main_window.show_message("Pages rotated successfully", "success")
            show_success("Success", f"Pages rotated successfully:\n{output}")

        def on_error(error):
            progress.error("Rotation failed")
            self.main_window.show_message("Rotation failed", "error")
            show_error("Error", f"Error rotating pages:\n{error}")

        worker = PDFWorker(
            operation="rotate",
            params={
                "input_pdf": self.input_file,
                "output_pdf": output,
                "angle": angle,
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
        self.pages_entry.config(state=tk.NORMAL)
        self.pages_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.page_mode.set("all")
        self.angle_var.set("90")
        self.pages_entry.config(state=tk.DISABLED)
        self.file_info_label.config(text="No file selected", fg=COLORS["text_secondary"])
        self._update_start_button()
        self.main_window.show_message("Reset", "info")
