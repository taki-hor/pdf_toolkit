"""
PDF info dialog for viewing PDF metadata and properties.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

from gui.widgets.progress_dialog import ProgressDialog
from gui.workers.pdf_worker import PDFWorker
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import select_pdf_file, show_error


class InfoDialog(tk.Frame):
    """
    Dialog for viewing PDF information and metadata.
    """

    def __init__(self, parent, main_window):
        """
        Initialize info dialog.

        Args:
            parent: Parent widget
            main_window: Reference to main window
        """
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.input_file = None
        self.pdf_info = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Title
        title_label = tk.Label(
            self,
            text=f"{get_icon('info')} PDF Info",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="View detailed information and metadata of PDF files",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=(0, SPACING["medium"]))

        # Input file selection
        input_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        input_frame.pack(fill=tk.X, pady=SPACING["medium"])

        tk.Label(
            input_frame,
            text="Select File:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame,
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
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["small"])

        browse_btn = tk.Button(
            input_frame,
            text=f"{get_icon('folder')} Select File",
            command=self._select_file,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT)

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        # Info display area
        self.info_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=SPACING["medium"])

        # Show placeholder
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Show placeholder when no file is selected."""
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        placeholder_frame = tk.Frame(self.info_frame, bg=COLORS["bg_secondary"])
        placeholder_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        icon_label = tk.Label(
            placeholder_frame,
            text="[PDF]",
            font=("Arial", 36, "bold"),
            bg=COLORS["bg_secondary"]
        )
        icon_label.pack(pady=(0, 20))

        text_label = tk.Label(
            placeholder_frame,
            text="Select a PDF file to view information",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        text_label.pack()

    def _select_file(self) -> None:
        """Select PDF file and show info."""
        filepath = select_pdf_file()
        if not filepath:
            return

        self.input_file = filepath
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filepath)
        self.input_entry.config(state="readonly")

        # Get PDF info
        self._load_info()

    def _load_info(self) -> None:
        """Load and display PDF info."""
        if not self.input_file:
            return

        # Show progress
        progress = ProgressDialog(self, title="Load Info")
        progress.update_status("Reading PDF information...")

        # Start worker thread
        def on_complete(result):
            progress.complete("Load complete!")
            self.pdf_info = result
            self._display_info()
            self.main_window.show_message("Information loaded", "success")

        def on_error(error):
            progress.error("Load failed")
            self.main_window.show_message("Load failed", "error")
            show_error("Error", f"Error reading PDF information:\n{error}")
            self._show_placeholder()

        worker = PDFWorker(
            operation="info",
            params={"input_pdf": self.input_file},
            on_complete=on_complete,
            on_error=on_error
        )
        worker.start()

    def _display_info(self) -> None:
        """Display PDF info in the info area."""
        if not self.pdf_info:
            return

        # Clear existing content
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Create scrollable frame
        canvas = tk.Canvas(self.info_frame, bg=COLORS["bg_secondary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_secondary"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display info sections
        self._add_section(scrollable_frame, "[PDF] Basic Info", {
            "Filename": self.pdf_info.get("filename", "N/A"),
            "File Size": self.pdf_info.get("file_size", "N/A"),
        })

        self._add_section(scrollable_frame, "[DOC] Document Properties", {
            "Pages": f"{self.pdf_info.get('page_count', 'N/A')} pages",
            "PDF Version": self.pdf_info.get("pdf_version", "N/A"),
            "Encrypted": "Yes" if self.pdf_info.get("is_encrypted", False) else "No",
        })

        self._add_section(scrollable_frame, "[META] Metadata", {
            "Title": self.pdf_info.get("title", "N/A"),
            "Author": self.pdf_info.get("author", "N/A"),
            "Subject": self.pdf_info.get("subject", "N/A"),
            "Keywords": self.pdf_info.get("keywords", "N/A"),
            "Creator": self.pdf_info.get("creator", "N/A"),
            "Producer": self.pdf_info.get("producer", "N/A"),
            "Creation Date": self.pdf_info.get("creation_date", "N/A"),
            "Modification Date": self.pdf_info.get("mod_date", "N/A"),
        })

        # Copy button
        button_frame = tk.Frame(scrollable_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X, pady=SPACING["large"])

        copy_btn = tk.Button(
            button_frame,
            text="Copy All Info",
            command=self._copy_info,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        copy_btn.pack()

    def _add_section(self, parent, title: str, items: dict) -> None:
        """
        Add an info section.

        Args:
            parent: Parent widget
            title: Section title
            items: Dictionary of key-value pairs
        """
        section_frame = tk.LabelFrame(
            parent,
            text=title,
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        section_frame.pack(fill=tk.X, pady=SPACING["medium"], padx=SPACING["small"])

        for key, value in items.items():
            row_frame = tk.Frame(section_frame, bg=COLORS["bg_secondary"])
            row_frame.pack(fill=tk.X, pady=SPACING["small"])

            key_label = tk.Label(
                row_frame,
                text=f"{key}:",
                font=FONTS["default"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_secondary"],
                width=12,
                anchor=tk.W
            )
            key_label.pack(side=tk.LEFT)

            value_label = tk.Label(
                row_frame,
                text=str(value),
                font=FONTS["default"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_primary"],
                anchor=tk.W,
                wraplength=400,
                justify=tk.LEFT
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _copy_info(self) -> None:
        """Copy all info to clipboard."""
        if not self.pdf_info:
            return

        # Format info as text
        text_lines = ["PDF Information", "=" * 50, ""]

        text_lines.append("Basic Info:")
        text_lines.append(f"  Filename: {self.pdf_info.get('filename', 'N/A')}")
        text_lines.append(f"  File Size: {self.pdf_info.get('file_size', 'N/A')}")
        text_lines.append("")

        text_lines.append("Document Properties:")
        text_lines.append(f"  Pages: {self.pdf_info.get('page_count', 'N/A')} pages")
        text_lines.append(f"  PDF Version: {self.pdf_info.get('pdf_version', 'N/A')}")
        text_lines.append(f"  Encrypted: {'Yes' if self.pdf_info.get('is_encrypted', False) else 'No'}")
        text_lines.append("")

        text_lines.append("Metadata:")
        text_lines.append(f"  Title: {self.pdf_info.get('title', 'N/A')}")
        text_lines.append(f"  Author: {self.pdf_info.get('author', 'N/A')}")
        text_lines.append(f"  Subject: {self.pdf_info.get('subject', 'N/A')}")
        text_lines.append(f"  Creator: {self.pdf_info.get('creator', 'N/A')}")
        text_lines.append(f"  Producer: {self.pdf_info.get('producer', 'N/A')}")
        text_lines.append(f"  Creation Date: {self.pdf_info.get('creation_date', 'N/A')}")
        text_lines.append(f"  Modification Date: {self.pdf_info.get('mod_date', 'N/A')}")

        text = "\n".join(text_lines)

        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(text)
        self.main_window.show_message("Information copied to clipboard", "success")
