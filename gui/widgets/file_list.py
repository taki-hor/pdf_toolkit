"""
File list widget with drag and drop support.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import List, Optional, Callable
import fitz  # PyMuPDF

from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import select_pdf_files, get_file_info


class FileListWidget(tk.Frame):
    """
    Widget for displaying and managing a list of PDF files.
    Supports selection, reordering, and basic file operations.
    """

    def __init__(
        self,
        parent,
        on_files_changed: Optional[Callable] = None,
        allow_multiple: bool = True,
        show_page_count: bool = True
    ):
        """
        Initialize file list widget.

        Args:
            parent: Parent widget
            on_files_changed: Callback when file list changes
            allow_multiple: Whether to allow multiple file selection
            show_page_count: Whether to show page count for each file
        """
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.on_files_changed = on_files_changed
        self.allow_multiple = allow_multiple
        self.show_page_count = show_page_count
        self.files: List[Path] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        # Title
        title_label = tk.Label(
            self,
            text=f"{get_icon('file')} File List",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(SPACING["small"], SPACING["medium"]))

        # Listbox with scrollbar
        list_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["medium"], pady=SPACING["small"])

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=FONTS["default"],
            height=8,
            selectmode=tk.EXTENDED if self.allow_multiple else tk.SINGLE,
            bg="white",
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground="white",
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Button panel
        btn_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        btn_frame.pack(fill=tk.X, padx=SPACING["medium"], pady=SPACING["medium"])

        # Add button
        add_btn = self._create_button(
            btn_frame,
            f"{get_icon('add')} Add Files",
            self._add_files,
            COLORS["accent"]
        )
        add_btn.pack(side=tk.LEFT, padx=SPACING["small"])

        # Remove button
        remove_btn = self._create_button(
            btn_frame,
            f"{get_icon('remove')} Remove",
            self._remove_selected,
            COLORS["error"]
        )
        remove_btn.pack(side=tk.LEFT, padx=SPACING["small"])

        # Clear button
        clear_btn = self._create_button(
            btn_frame,
            "Clear",
            self.clear,
            COLORS["border"]
        )
        clear_btn.pack(side=tk.LEFT, padx=SPACING["small"])

        # Info label
        self.info_label = tk.Label(
            self,
            text="No files selected",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        self.info_label.pack(pady=SPACING["small"])

    def _create_button(self, parent, text: str, command: Callable, bg_color: str) -> tk.Button:
        """Create a styled button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg="white",
            font=FONTS["button"],
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            borderwidth=0
        )
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent_hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        return btn

    def _add_files(self) -> None:
        """Open file dialog to add PDF files."""
        files = select_pdf_files()
        for file in files:
            self.add_file(file)

    def _remove_selected(self) -> None:
        """Remove selected files from list."""
        selection = self.listbox.curselection()
        if not selection:
            return

        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.listbox.delete(index)
            del self.files[index]

        self._update_info()
        self._notify_change()

    def add_file(self, filepath: str) -> bool:
        """
        Add a file to the list.

        Args:
            filepath: Path to PDF file

        Returns:
            True if file was added, False if already in list or invalid
        """
        path = Path(filepath)

        # Validate
        if not path.exists():
            return False

        if not path.suffix.lower() == '.pdf':
            return False

        if path in self.files:
            return False

        # Add to list
        self.files.append(path)

        # Get page count if needed
        page_info = ""
        if self.show_page_count:
            try:
                doc = fitz.open(str(path))
                page_count = doc.page_count
                doc.close()
                page_info = f" ({page_count} pages)"
            except Exception:
                page_info = ""

        # Add to listbox
        display_name = f"{get_icon('file')} {path.name}{page_info}"
        self.listbox.insert(tk.END, display_name)

        self._update_info()
        self._notify_change()
        return True

    def clear(self) -> None:
        """Clear all files from list."""
        self.listbox.delete(0, tk.END)
        self.files.clear()
        self._update_info()
        self._notify_change()

    def get_files(self) -> List[str]:
        """Get list of file paths."""
        return [str(f) for f in self.files]

    def get_selected_files(self) -> List[str]:
        """Get list of selected file paths."""
        selection = self.listbox.curselection()
        return [str(self.files[i]) for i in selection]

    def _update_info(self) -> None:
        """Update info label."""
        count = len(self.files)
        if count == 0:
            self.info_label.config(text="No files selected")
        elif count == 1:
            self.info_label.config(text=f"Selected {count} file")
        else:
            self.info_label.config(text=f"Selected {count} files")

    def _notify_change(self) -> None:
        """Notify callback of file list change."""
        if self.on_files_changed:
            self.on_files_changed(self.get_files())
