"""
Helper utilities for PDF Toolkit GUI.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from typing import List, Optional


def show_error(title: str, message: str) -> None:
    """Display error dialog."""
    messagebox.showerror(title, message)


def show_warning(title: str, message: str) -> None:
    """Display warning dialog."""
    messagebox.showwarning(title, message)


def show_info(title: str, message: str) -> None:
    """Display information dialog."""
    messagebox.showinfo(title, message)


def show_success(title: str, message: str) -> None:
    """Display success dialog."""
    messagebox.showinfo(title, message)


def confirm(title: str, message: str) -> bool:
    """Display confirmation dialog and return user choice."""
    return messagebox.askyesno(title, message)


def select_pdf_files(title: str = "Select PDF Files") -> List[str]:
    """
    Open file dialog to select PDF files.

    Args:
        title: Dialog title

    Returns:
        List of selected file paths
    """
    files = filedialog.askopenfilenames(
        title=title,
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )
    return list(files) if files else []


def select_pdf_file(title: str = "Select PDF File") -> Optional[str]:
    """
    Open file dialog to select a single PDF file.

    Args:
        title: Dialog title

    Returns:
        Selected file path or None
    """
    file = filedialog.askopenfilename(
        title=title,
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )
    return file if file else None


def select_save_file(title: str = "Save PDF File", default_name: str = "output.pdf") -> Optional[str]:
    """
    Open save file dialog.

    Args:
        title: Dialog title
        default_name: Default filename

    Returns:
        Selected file path or None
    """
    file = filedialog.asksaveasfilename(
        title=title,
        defaultextension=".pdf",
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ],
        initialfile=default_name
    )
    return file if file else None


def select_directory(title: str = "Select Folder") -> Optional[str]:
    """
    Open directory selection dialog.

    Args:
        title: Dialog title

    Returns:
        Selected directory path or None
    """
    directory = filedialog.askdirectory(title=title)
    return directory if directory else None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_file_info(filepath: str) -> dict:
    """
    Get basic file information.

    Args:
        filepath: Path to file

    Returns:
        Dictionary with file information
    """
    path = Path(filepath)
    if not path.exists():
        return {}

    stat = path.stat()
    return {
        "name": path.name,
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "path": str(path.resolve()),
    }


def center_window(window: tk.Toplevel, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """
    Center a window on the screen.

    Args:
        window: Window to center
        width: Window width (uses current if None)
        height: Window height (uses current if None)
    """
    window.update_idletasks()

    if width is None or height is None:
        width = window.winfo_width()
        height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
