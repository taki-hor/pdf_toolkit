"""OCR dialog for batch processing scanned PDFs."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from core import PDFOCRExtractor
from gui.widgets.progress_dialog import ProgressDialog
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import select_directory, show_error, show_success


class OCRDialog(tk.Frame):
    """Dialog that manages OCR extraction and indexing."""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.extractor = PDFOCRExtractor()
        self.progress_dialog: ProgressDialog | None = None
        self.worker: threading.Thread | None = None

        self.folder_var = tk.StringVar()
        self.lang_var = tk.StringVar(value=PDFOCRExtractor.DEFAULT_LANG)
        self.dpi_var = tk.IntVar(value=300)
        self.recursive_var = tk.BooleanVar(value=False)
        self.force_var = tk.BooleanVar(value=False)
        self.use_cache_var = tk.BooleanVar(value=True)
        self.ocrmypdf_var = tk.BooleanVar(value=False)

        self._setup_ui()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        title = tk.Label(
            self,
            text=f"{get_icon('ocr')} OCR Extract",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        title.pack(pady=(0, SPACING["large"]))

        desc = tk.Label(
            self,
            text="Convert scanned PDFs into searchable text and index results",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
        )
        desc.pack(pady=(0, SPACING["medium"]))

        folder_frame = tk.LabelFrame(
            self,
            text="Source Folder",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"],
        )
        folder_frame.pack(fill=tk.X, pady=SPACING["medium"])

        select_frame = tk.Frame(folder_frame, bg=COLORS["bg_secondary"])
        select_frame.pack(fill=tk.X)

        self.folder_entry = tk.Entry(
            select_frame,
            textvariable=self.folder_var,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            state="readonly",
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["small"]))

        browse_btn = tk.Button(
            select_frame,
            text=f"{get_icon('folder')} Select Folder",
            command=self._select_folder,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=18,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
        )
        browse_btn.pack(side=tk.LEFT)

        options_frame = tk.LabelFrame(
            self,
            text="OCR Settings",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"],
        )
        options_frame.pack(fill=tk.X, pady=SPACING["medium"])

        lang_row = tk.Frame(options_frame, bg=COLORS["bg_secondary"])
        lang_row.pack(fill=tk.X, pady=(0, SPACING["small"]))

        tk.Label(
            lang_row,
            text="Language:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        lang_combo = ttk.Combobox(
            lang_row,
            textvariable=self.lang_var,
            values=[
                "chi_tra+eng",
                "chi_sim+eng",
                "eng",
                "jpn",
            ],
            font=FONTS["default"],
            state="readonly",
        )
        lang_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        dpi_row = tk.Frame(options_frame, bg=COLORS["bg_secondary"])
        dpi_row.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            dpi_row,
            text="Render DPI:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=12,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        dpi_spin = tk.Spinbox(
            dpi_row,
            from_=150,
            to=600,
            increment=50,
            textvariable=self.dpi_var,
            font=FONTS["default"],
            width=6,
        )
        dpi_spin.pack(side=tk.LEFT, padx=(0, SPACING["medium"]))

        self.recursive_check = tk.Checkbutton(
            options_frame,
            text="Include subdirectories",
            variable=self.recursive_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
        )
        self.recursive_check.pack(anchor=tk.W, pady=2)

        self.force_check = tk.Checkbutton(
            options_frame,
            text="Force re-index even if cached",
            variable=self.force_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
        )
        self.force_check.pack(anchor=tk.W, pady=2)

        self.cache_check = tk.Checkbutton(
            options_frame,
            text="Use OCR cache",
            variable=self.use_cache_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
        )
        self.cache_check.pack(anchor=tk.W, pady=2)

        self.ocrmypdf_check = tk.Checkbutton(
            options_frame,
            text="Use ocrmypdf backend (slower, better quality)",
            variable=self.ocrmypdf_var,
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            selectcolor="white",
            activebackground=COLORS["bg_secondary"],
            activeforeground=COLORS["text_primary"],
        )
        self.ocrmypdf_check.pack(anchor=tk.W, pady=2)

        action_frame = tk.Frame(self, bg=COLORS["bg_secondary"])
        action_frame.pack(fill=tk.X, pady=SPACING["medium"])

        self.start_btn = tk.Button(
            action_frame,
            text=f"{get_icon('rocket')} Start OCR",
            command=self._start_ocr,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=26,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.start_btn.pack(side=tk.RIGHT, padx=(SPACING["small"], 0))

        export_btn = tk.Button(
            action_frame,
            text=f"{get_icon('save')} Export Index",
            command=self._export_index,
            bg=COLORS["border"],
            fg=COLORS["text_primary"],
            font=FONTS["button"],
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
        )
        export_btn.pack(side=tk.RIGHT, padx=(0, SPACING["small"]))

        output_frame = tk.LabelFrame(
            self,
            text="Activity Log",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["small"],
        )
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.summary_text = tk.Text(
            output_frame,
            height=12,
            font=("DejaVu Sans Mono", 10),
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.summary_text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(output_frame, command=self.summary_text.yview)
        self.summary_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _select_folder(self) -> None:
        folder = select_directory("Select folder containing PDFs")
        if folder:
            self.folder_var.set(folder)
            self.start_btn.config(state=tk.NORMAL)
            self.main_window.show_message("Folder selected, ready to run OCR", "info")

    def _start_ocr(self) -> None:
        folder = self.folder_var.get().strip()
        if not folder:
            show_error("Missing folder", "請先選擇要處理的資料夾。")
            return

        if self.worker and self.worker.is_alive():
            return  # already running

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, "Starting OCR...\n")
        self.summary_text.config(state=tk.DISABLED)

        self.progress_dialog = ProgressDialog(self, title="Running OCR")
        self.start_btn.config(state=tk.DISABLED)
        self.main_window.show_message("OCR processing started", "info")

        params = {
            "folder": folder,
            "lang": self.lang_var.get().strip() or PDFOCRExtractor.DEFAULT_LANG,
            "dpi": int(self.dpi_var.get()),
            "recursive": self.recursive_var.get(),
            "force": self.force_var.get(),
            "use_cache": self.use_cache_var.get(),
            "use_ocrmypdf": self.ocrmypdf_var.get(),
        }

        self.worker = threading.Thread(
            target=self._run_ocr,
            args=(params,),
            daemon=True,
        )
        self.worker.start()

    def _run_ocr(self, params: dict) -> None:
        try:
            summary = self.extractor.batch_ocr_folder(
                params["folder"],
                lang=params["lang"],
                dpi=params["dpi"],
                recursive=params["recursive"],
                force=params["force"],
                use_cache=params["use_cache"],
                use_ocrmypdf=params["use_ocrmypdf"],
                progress_callback=self._handle_progress,
            )
        except Exception as exc:  # pragma: no cover - runtime protection
            self.after(0, lambda: self._on_ocr_error(str(exc)))
        else:
            self.after(0, lambda: self._on_ocr_complete(summary))

    def _handle_progress(
        self,
        index: int,
        total: int,
        pdf_path: Path,
        status: str,
        message: str,
    ) -> None:
        def update_ui() -> None:
            if self.progress_dialog:
                total_safe = total if total else 1
                completed = index if status in {"success", "skip", "error"} else max(0, index - 1)
                percent = min(100.0, (completed / total_safe) * 100)
                status_map = {
                    "start": "Processing",
                    "success": "Done",
                    "skip": "Skipped",
                    "error": "Error",
                }
                label = status_map.get(status, status)
                self.progress_dialog.update_status(
                    f"{label}: {pdf_path.name}",
                    detail=message,
                )
                self.progress_dialog.set_progress(percent)

            log_prefix = {
                "start": "➡",
                "success": "✅",
                "skip": "⏭",
                "error": "❌",
            }.get(status, "•")
            self._append_log(f"{log_prefix} {pdf_path.name} - {message}")

        self.after(0, update_ui)

    def _append_log(self, text: str) -> None:
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.insert(tk.END, text + "\n")
        self.summary_text.see(tk.END)
        self.summary_text.config(state=tk.DISABLED)

    def _on_ocr_complete(self, summary: dict) -> None:
        if self.progress_dialog:
            self.progress_dialog.complete("完成")
            self.progress_dialog = None

        self.start_btn.config(state=tk.NORMAL)
        self.main_window.show_message("OCR completed", "success")

        report = [
            "",
            f"Processed: {summary.get('indexed', 0)} files",
            f"Updated: {summary.get('updated', 0)} files",
            f"Skipped: {summary.get('skipped', 0)} files",
            f"Duration: {summary.get('duration', 0.0):.2f} seconds",
        ]
        if summary.get("errors"):
            report.append("Errors:")
            for item in summary["errors"]:
                report.append(f" - {item.get('file')}: {item.get('error')}")

        for line in report:
            self._append_log(line)

        show_success("完成", "OCR 索引建立完成！")

    def _on_ocr_error(self, message: str) -> None:
        if self.progress_dialog:
            self.progress_dialog.error("發生錯誤")
            self.progress_dialog = None
        self.start_btn.config(state=tk.NORMAL)
        self.main_window.show_message("OCR failed", "error")
        self._append_log(f"❌ Error: {message}")
        show_error("OCR 失敗", message)

    def _export_index(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Export OCR Index",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            initialfile="index_export.json",
        )
        if not output:
            return

        try:
            exported = self.extractor.export_index(output)
        except Exception as exc:  # pragma: no cover - user feedback
            show_error("匯出失敗", str(exc))
            return

        self._append_log(f"📤 Index exported to {exported}")
        show_success("匯出完成", f"索引已匯出至：{exported}")
        self.main_window.show_message("Index exported", "success")
