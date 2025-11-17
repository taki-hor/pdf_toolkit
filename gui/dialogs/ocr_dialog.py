"""
OCR dialog for extracting text from scanned PDFs.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import fitz  # PyMuPDF

from gui.widgets.progress_dialog import ProgressDialog
from gui.workers.pdf_worker import PDFWorker
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import (
    select_pdf_file, show_success, show_error, show_warning
)


class OCRDialog(tk.Frame):
    """
    Dialog for OCR text extraction from scanned PDFs.
    """

    # Common OCR languages
    LANGUAGES = [
        ("English", "eng"),
        ("Simplified Chinese", "chi_sim"),
        ("Traditional Chinese", "chi_tra"),
        ("French", "fra"),
        ("German", "deu"),
        ("Spanish", "spa"),
        ("Japanese", "jpn"),
        ("Korean", "kor"),
        ("Arabic", "ara"),
        ("Russian", "rus"),
        ("Portuguese", "por"),
        ("Italian", "ita"),
    ]

    def __init__(self, parent, main_window):
        """
        Initialize OCR dialog.

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
            text=f"{get_icon('document')} OCR Text Extraction",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, SPACING["large"]))

        # Description
        desc_label = tk.Label(
            self,
            text="Extract text from scanned PDFs using OCR (Optical Character Recognition)",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=(0, SPACING["medium"]))

        # Input file selection
        input_frame = tk.LabelFrame(
            self,
            text="Source PDF",
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

        # OCR Settings
        settings_frame = tk.LabelFrame(
            self,
            text="OCR Settings",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        settings_frame.pack(fill=tk.X, pady=SPACING["medium"])

        # Language selection
        lang_frame = tk.Frame(settings_frame, bg=COLORS["bg_secondary"])
        lang_frame.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            lang_frame,
            text="Language:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.language_var = tk.StringVar(value="eng")
        language_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=[f"{name} ({code})" for name, code in self.LANGUAGES],
            state="readonly",
            font=FONTS["default"],
            width=25
        )
        language_combo.pack(side=tk.LEFT, padx=SPACING["small"])
        language_combo.set("English (eng)")

        # DPI selection
        dpi_frame = tk.Frame(settings_frame, bg=COLORS["bg_secondary"])
        dpi_frame.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            dpi_frame,
            text="DPI Quality:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.dpi_var = tk.IntVar(value=300)
        dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=[150, 200, 300, 400, 600],
            state="readonly",
            font=FONTS["default"],
            width=10
        )
        dpi_combo.pack(side=tk.LEFT, padx=SPACING["small"])
        dpi_combo.set(300)

        tk.Label(
            dpi_frame,
            text="(Higher = better quality but slower)",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        ).pack(side=tk.LEFT, padx=SPACING["small"])

        # Output formats
        output_frame = tk.LabelFrame(
            self,
            text="Output Formats (select at least one)",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )
        output_frame.pack(fill=tk.X, pady=SPACING["medium"])

        # DOCX output
        self.docx_var = tk.BooleanVar(value=True)
        docx_check = tk.Checkbutton(
            output_frame,
            text="Microsoft Word (.docx)",
            variable=self.docx_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_format_change
        )
        docx_check.pack(anchor=tk.W, pady=SPACING["small"])

        docx_path_frame = tk.Frame(output_frame, bg=COLORS["bg_secondary"])
        docx_path_frame.pack(fill=tk.X, padx=(25, 0), pady=(0, SPACING["small"]))

        self.docx_entry = tk.Entry(
            docx_path_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        self.docx_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        docx_browse = tk.Button(
            docx_path_frame,
            text=f"{get_icon('folder')} Browse",
            command=lambda: self._select_output_file("docx"),
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=10,
            pady=3,
            relief=tk.FLAT,
            cursor="hand2"
        )
        docx_browse.pack(side=tk.LEFT)

        # ODT output
        self.odt_var = tk.BooleanVar(value=False)
        odt_check = tk.Checkbutton(
            output_frame,
            text="LibreOffice Writer (.odt)",
            variable=self.odt_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_format_change
        )
        odt_check.pack(anchor=tk.W, pady=SPACING["small"])

        odt_path_frame = tk.Frame(output_frame, bg=COLORS["bg_secondary"])
        odt_path_frame.pack(fill=tk.X, padx=(25, 0), pady=(0, SPACING["small"]))

        self.odt_entry = tk.Entry(
            odt_path_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            state=tk.DISABLED
        )
        self.odt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        odt_browse = tk.Button(
            odt_path_frame,
            text=f"{get_icon('folder')} Browse",
            command=lambda: self._select_output_file("odt"),
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=10,
            pady=3,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        odt_browse.pack(side=tk.LEFT)
        self.odt_browse_btn = odt_browse

        # TXT output
        self.txt_var = tk.BooleanVar(value=False)
        txt_check = tk.Checkbutton(
            output_frame,
            text="Plain Text (.txt)",
            variable=self.txt_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
            command=self._on_format_change
        )
        txt_check.pack(anchor=tk.W, pady=SPACING["small"])

        txt_path_frame = tk.Frame(output_frame, bg=COLORS["bg_secondary"])
        txt_path_frame.pack(fill=tk.X, padx=(25, 0), pady=(0, SPACING["small"]))

        self.txt_entry = tk.Entry(
            txt_path_frame,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            state=tk.DISABLED
        )
        self.txt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        txt_browse = tk.Button(
            txt_path_frame,
            text=f"{get_icon('folder')} Browse",
            command=lambda: self._select_output_file("txt"),
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=10,
            pady=3,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        txt_browse.pack(side=tk.LEFT)
        self.txt_browse_btn = txt_browse

        # Warning about Tesseract
        warning_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        warning_frame.pack(fill=tk.X, pady=SPACING["medium"])

        warning_label = tk.Label(
            warning_frame,
            text=f"{get_icon('info')} Note: Tesseract OCR must be installed on your system",
            font=("Arial", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            anchor=tk.W
        )
        warning_label.pack(fill=tk.X)

        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X, pady=SPACING["large"])

        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text=f"{get_icon('rocket')} Start OCR",
            command=self._start_ocr,
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
                text=f"{self.page_count} page(s) - Ready for OCR",
                fg=COLORS["text_primary"]
            )
        except Exception as e:
            self.file_info_label.config(
                text=f"Error reading file: {e}",
                fg="red"
            )
            self.input_file = None

        # Auto-populate output paths
        if self.input_file:
            base_path = Path(filepath).stem
            parent_dir = Path(filepath).parent

            if self.docx_var.get() and not self.docx_entry.get():
                self.docx_entry.delete(0, tk.END)
                self.docx_entry.insert(0, str(parent_dir / f"{base_path}_ocr.docx"))

        self._update_start_button()

    def _select_output_file(self, format_type: str) -> None:
        """Select output file for specific format."""
        extensions = {
            "docx": ("Word Document", "*.docx"),
            "odt": ("LibreOffice Document", "*.odt"),
            "txt": ("Text File", "*.txt")
        }

        filetypes = [extensions[format_type], ("All Files", "*.*")]

        filepath = filedialog.asksaveasfilename(
            title=f"Save {format_type.upper()} Output",
            filetypes=filetypes,
            defaultextension=f".{format_type}"
        )

        if filepath:
            entry = getattr(self, f"{format_type}_entry")
            entry.delete(0, tk.END)
            entry.insert(0, filepath)
            self._update_start_button()

    def _on_format_change(self) -> None:
        """Handle output format checkbox changes."""
        # Enable/disable DOCX entry
        if self.docx_var.get():
            self.docx_entry.config(state=tk.NORMAL)
        else:
            self.docx_entry.config(state=tk.DISABLED)

        # Enable/disable ODT entry
        if self.odt_var.get():
            self.odt_entry.config(state=tk.NORMAL)
            self.odt_browse_btn.config(state=tk.NORMAL)
        else:
            self.odt_entry.config(state=tk.DISABLED)
            self.odt_browse_btn.config(state=tk.DISABLED)

        # Enable/disable TXT entry
        if self.txt_var.get():
            self.txt_entry.config(state=tk.NORMAL)
            self.txt_browse_btn.config(state=tk.NORMAL)
        else:
            self.txt_entry.config(state=tk.DISABLED)
            self.txt_browse_btn.config(state=tk.DISABLED)

        self._update_start_button()

    def _update_start_button(self) -> None:
        """Update start button state."""
        has_input = self.input_file is not None
        has_output = False

        # Check if at least one format is selected with a path
        if self.docx_var.get() and self.docx_entry.get().strip():
            has_output = True
        if self.odt_var.get() and self.odt_entry.get().strip():
            has_output = True
        if self.txt_var.get() and self.txt_entry.get().strip():
            has_output = True

        self.start_btn.config(
            state=tk.NORMAL if (has_input and has_output) else tk.DISABLED
        )

    def _get_language_code(self) -> str:
        """Extract language code from selected language."""
        selected = self.language_var.get()
        # Extract code from "Language Name (code)" format
        if "(" in selected and ")" in selected:
            return selected.split("(")[1].split(")")[0]
        return "eng"

    def _start_ocr(self) -> None:
        """Start OCR operation."""
        if not self.input_file:
            show_error("Error", "Please select a PDF file")
            return

        # Check that at least one output format is selected
        if not (self.docx_var.get() or self.odt_var.get() or self.txt_var.get()):
            show_error("Error", "Please select at least one output format")
            return

        # Collect output paths
        params = {
            "input_pdf": self.input_file,
            "language": self._get_language_code(),
            "dpi": self.dpi_var.get()
        }

        if self.docx_var.get():
            docx_path = self.docx_entry.get().strip()
            if docx_path:
                params["output_docx"] = docx_path

        if self.odt_var.get():
            odt_path = self.odt_entry.get().strip()
            if odt_path:
                params["output_odt"] = odt_path

        if self.txt_var.get():
            txt_path = self.txt_entry.get().strip()
            if txt_path:
                params["output_txt"] = txt_path

        # Show progress dialog
        progress = ProgressDialog(self, title="OCR Processing")
        progress.update_status(f"Performing OCR on {self.page_count} page(s)...\nThis may take a while...")

        # Start worker thread
        def on_complete(result):
            progress.complete("OCR complete!")
            self.main_window.show_message("OCR complete", "success")

            # Build success message
            outputs = []
            if params.get("output_docx"):
                outputs.append(f"DOCX: {params['output_docx']}")
            if params.get("output_odt"):
                outputs.append(f"ODT: {params['output_odt']}")
            if params.get("output_txt"):
                outputs.append(f"TXT: {params['output_txt']}")

            msg = "OCR text extraction completed successfully!\n\nOutput files:\n" + "\n".join(outputs)
            show_success("Success", msg)

        def on_error(error):
            progress.error("OCR failed")
            self.main_window.show_message("OCR failed", "error")
            show_error("Error", f"OCR extraction failed:\n{error}")

        worker = PDFWorker(
            operation="ocr",
            params=params,
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
        self.docx_entry.delete(0, tk.END)
        self.odt_entry.delete(0, tk.END)
        self.txt_entry.delete(0, tk.END)
        self.docx_var.set(True)
        self.odt_var.set(False)
        self.txt_var.set(False)
        self.language_var.set("eng")
        self.dpi_var.set(300)
        self.file_info_label.config(text="No file selected", fg=COLORS["text_secondary"])
        self._on_format_change()
        self._update_start_button()
        self.main_window.show_message("Reset", "info")
