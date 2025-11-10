"""Tkinter dialog for the PDF diff tool."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils import helpers


class PDFDiffDialog(tk.Frame):
    """Interactive UI for comparing PDF documents."""

    def __init__(self, parent, main_window) -> None:
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.old_path_var = tk.StringVar()
        self.new_path_var = tk.StringVar()
        self._tool = None
        self._last_result = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create dialog widgets."""
        title = tk.Label(
            self,
            text=f"{get_icon('info')} PDF Diff",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        title.pack(anchor=tk.W, pady=(0, SPACING["medium"]))

        description = tk.Label(
            self,
            text="Compare two PDF versions and review key changes.",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
        )
        description.pack(anchor=tk.W, pady=(0, SPACING["medium"]))

        self._build_file_selector(
            label="Old PDF:",
            textvariable=self.old_path_var,
            command=lambda: self._browse_pdf(self.old_path_var),
        )
        self._build_file_selector(
            label="New PDF:",
            textvariable=self.new_path_var,
            command=lambda: self._browse_pdf(self.new_path_var),
        )

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=SPACING["medium"])

        button_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X, pady=(0, SPACING["medium"]))

        self.export_btn = tk.Button(
            button_frame,
            text=f"{get_icon('save')} Export HTML Report",
            command=self._export_report,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.export_btn.pack(side=tk.RIGHT)

        run_btn = tk.Button(
            button_frame,
            text=f"{get_icon('rocket')} Run Comparison",
            command=self._run_diff,
            bg=COLORS["accent"],
            fg="white",
            font=(FONTS["button"][0], 12, "bold"),
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
        )
        run_btn.pack(side=tk.RIGHT, padx=(0, SPACING["small"]))

        summary_label = tk.Label(
            self,
            text="Summary:",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        summary_label.pack(anchor=tk.W)

        summary_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        summary_frame.pack(fill=tk.BOTH, expand=True)

        self.summary_text = tk.Text(
            summary_frame,
            height=14,
            font=FONTS["mono"],
            bg="#fdfdfd",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text.configure(yscrollcommand=scrollbar.set)

    def _build_file_selector(self, label: str, textvariable: tk.StringVar, command) -> None:
        """Create file selection row."""
        frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        frame.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            frame,
            text=label,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        entry = tk.Entry(
            frame,
            textvariable=textvariable,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        browse_btn = tk.Button(
            frame,
            text=f"{get_icon('folder')} Browse",
            command=command,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            relief=tk.FLAT,
            cursor="hand2",
        )
        browse_btn.pack(side=tk.LEFT)

    def _browse_pdf(self, var: tk.StringVar) -> None:
        """Prompt for a PDF file and update *var*."""
        filepath = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
        )
        if filepath:
            var.set(filepath)

    def _run_diff(self) -> None:
        """Execute PDF comparison and render summary."""
        old_path = self.old_path_var.get().strip()
        new_path = self.new_path_var.get().strip()

        if not old_path or not new_path:
            helpers.show_warning("Files Required", "Please select both old and new PDF files.")
            return

        try:
            tool = self._ensure_tool()
            result = tool.compare_pdfs(Path(old_path), Path(new_path))
        except Exception as exc:  # pragma: no cover - runtime errors shown to user
            helpers.show_error("Comparison Failed", str(exc))
            self.main_window.show_message("PDF diff failed.", "error")
            return

        self._last_result = result
        self._render_summary(result)
        self.export_btn.config(state=tk.NORMAL)
        self.main_window.show_message("PDF comparison complete.", "success")

    def _render_summary(self, result) -> None:
        """Display diff summary in the text widget."""
        lines = [
            f"Similarity: {result.similarity:.2f}%",
            f"Added lines: {len(result.added)}",
            f"Deleted lines: {len(result.deleted)}",
            f"Modified pairs: {len(result.modified)}",
            "",
        ]

        if result.key_changes:
            lines.append("Key changes:")
            for key, values in result.key_changes.items():
                lines.append(f"- {key.title()}:")
                for entry in values:
                    lines.append(f"    • {entry}")
        else:
            lines.append("No notable key changes detected.")

        if result.added:
            lines.extend(["", "Added lines:"] + [f"+ {line}" for line in result.added[:10]])
            if len(result.added) > 10:
                lines.append("... (truncated)")
        if result.deleted:
            lines.extend(["", "Deleted lines:"] + [f"- {line}" for line in result.deleted[:10]])
            if len(result.deleted) > 10:
                lines.append("... (truncated)")

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", "\n".join(lines))
        self.summary_text.config(state=tk.DISABLED)

    def _export_report(self) -> None:
        """Save an HTML report using the latest diff result."""
        if not self._last_result:
            helpers.show_warning("No Results", "Run a comparison before exporting a report.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save HTML Report",
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        try:
            tool = self._ensure_tool()
            output = tool.generate_html_report(self._last_result, Path(filepath))
        except Exception as exc:  # pragma: no cover - runtime errors shown to user
            helpers.show_error("Export Failed", str(exc))
            return

        helpers.show_success("Report Saved", f"Report saved to {output}")
        self.main_window.show_message("HTML report generated.", "success")

    def _ensure_tool(self):
        """Initialise the PDF diff tool when required."""
        if self._tool is None:
            from core.pdf_diff_tool import PDFDiffTool

            self._tool = PDFDiffTool()
        return self._tool

