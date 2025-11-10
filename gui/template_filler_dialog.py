"""Tkinter dialog for the template filler feature."""

from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils import helpers


class TemplateFillerDialog(tk.Frame):
    """Interactive UI for filling DOCX/PDF templates."""

    def __init__(self, parent, main_window) -> None:
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.template_path_var = tk.StringVar()
        self.output_var = tk.StringVar(value="Output path will appear here")
        self._filler = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build dialog layout."""
        title = tk.Label(
            self,
            text=f"{get_icon('file')} Template Fill",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        title.pack(anchor=tk.W, pady=(0, SPACING["medium"]))

        description = tk.Label(
            self,
            text="Choose a template and provide placeholder data (JSON format).",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
        )
        description.pack(anchor=tk.W, pady=(0, SPACING["medium"]))

        # Template selection
        template_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        template_frame.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            template_frame,
            text="Template:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        entry = tk.Entry(
            template_frame,
            textvariable=self.template_path_var,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        browse_btn = tk.Button(
            template_frame,
            text=f"{get_icon('folder')} Browse",
            command=self._browse_template,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            relief=tk.FLAT,
            cursor="hand2",
        )
        browse_btn.pack(side=tk.LEFT)

        detect_btn = tk.Button(
            template_frame,
            text=f"{get_icon('preview')} Detect Fields",
            command=self._detect_fields,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            relief=tk.FLAT,
            cursor="hand2",
        )
        detect_btn.pack(side=tk.LEFT, padx=(SPACING["small"], 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        data_label = tk.Label(
            self,
            text="Placeholder data (JSON):",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        data_label.pack(anchor=tk.W)

        text_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=SPACING["small"])

        self.data_text = tk.Text(
            text_frame,
            height=12,
            font=FONTS["mono"],
            bg="#fdfdfd",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.data_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_text.configure(yscrollcommand=scrollbar.set)

        action_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        action_frame.pack(fill=tk.X, pady=SPACING["medium"])

        fill_btn = tk.Button(
            action_frame,
            text=f"{get_icon('rocket')} Fill Template",
            command=self._fill_template,
            bg=COLORS["accent"],
            fg="white",
            font=(FONTS["button"][0], 12, "bold"),
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
        )
        fill_btn.pack(side=tk.RIGHT)

        reset_btn = tk.Button(
            action_frame,
            text=f"{get_icon('refresh')} Clear",
            command=self._reset,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            relief=tk.FLAT,
            cursor="hand2",
        )
        reset_btn.pack(side=tk.RIGHT, padx=(0, SPACING["small"]))

        output_label = tk.Label(
            self,
            textvariable=self.output_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            wraplength=600,
            justify=tk.LEFT,
        )
        output_label.pack(fill=tk.X, pady=(SPACING["small"], 0))

    def _browse_template(self) -> None:
        """Open file dialog for selecting DOCX/PDF templates."""
        filepath = filedialog.askopenfilename(
            title="Select Template",
            filetypes=[
                ("Template Files", "*.docx *.pdf"),
                ("Word Document", "*.docx"),
                ("PDF", "*.pdf"),
                ("All Files", "*.*"),
            ],
        )
        if filepath:
            self.template_path_var.set(filepath)

    def _detect_fields(self) -> None:
        """Auto-detect placeholders for DOCX templates and populate JSON skeleton."""
        template = self.template_path_var.get().strip()
        if not template:
            helpers.show_warning("Template Required", "Please choose a DOCX template first.")
            return

        if not template.lower().endswith(".docx"):
            helpers.show_warning("Unsupported", "Field detection works with DOCX templates only.")
            return

        try:
            from core.template_filler import SmartFiller

            placeholders = SmartFiller.auto_detect_placeholders_from_docx(Path(template))
        except Exception as exc:  # pragma: no cover - runtime dependency errors
            helpers.show_error("Detection Failed", str(exc))
            return

        if not placeholders:
            helpers.show_info("No Placeholders", "No placeholders were detected in this document.")
            return

        sample_data = {
            field: SmartFiller.suggest_default_value(field) or ""
            for field in placeholders
        }
        self.data_text.delete("1.0", tk.END)
        self.data_text.insert("1.0", json.dumps(sample_data, indent=2))
        self.main_window.show_message("Placeholders detected and sample data generated.")

    def _reset(self) -> None:
        """Reset input fields."""
        self.template_path_var.set("")
        self.data_text.delete("1.0", tk.END)
        self.output_var.set("Output path will appear here")
        self.main_window.show_message("Template filler reset.")

    def _fill_template(self) -> None:
        """Trigger filling of the selected template."""
        template = self.template_path_var.get().strip()
        if not template:
            helpers.show_warning("Template Required", "Please choose a template to fill.")
            return

        raw_data = self.data_text.get("1.0", tk.END).strip()
        if not raw_data:
            helpers.show_warning("Data Required", "Provide JSON data for placeholders.")
            return

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as exc:
            helpers.show_error("Invalid JSON", f"Could not parse the provided data: {exc}")
            return

        suffix = Path(template).suffix.lower()
        try:
            filler = self._ensure_filler()
            if suffix == ".docx":
                output = filler.fill_docx_template(template, data)
            elif suffix == ".pdf":
                output = filler.fill_pdf_form(template, data)
            else:
                helpers.show_warning("Unsupported", "Only DOCX and PDF templates are supported.")
                return
        except Exception as exc:  # pragma: no cover - runtime errors forwarded to user
            helpers.show_error("Fill Failed", str(exc))
            self.main_window.show_message("Template fill failed.", "error")
            return

        self.output_var.set(f"Generated: {output}")
        helpers.show_success("Template Filled", f"File saved to {output}")
        self.main_window.show_message("Template filled successfully!", "success")

    def _ensure_filler(self):
        """Create TemplateFiller on demand."""
        if self._filler is None:
            from core.template_filler import TemplateFiller

            self._filler = TemplateFiller()
        return self._filler

