"""Search dialog for querying OCR index."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
from core import PDFOCRExtractor
from gui.utils.theme import COLORS, FONTS, SPACING
from gui.utils.icons import get_icon
from gui.utils.helpers import show_error, show_info


class SearchDialog(tk.Frame):
    """Dialog to search within OCR index."""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg=COLORS["bg_secondary"])
        self.main_window = main_window
        self.extractor = PDFOCRExtractor()
        self.worker: threading.Thread | None = None
        self.current_results: list[dict[str, object]] = []

        self.keyword_var = tk.StringVar()
        self.limit_var = tk.IntVar(value=20)
        self.context_var = tk.IntVar(value=80)
        self.status_var = tk.StringVar(value="Enter keyword and click search")

        self._setup_ui()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        title = tk.Label(
            self,
            text=f"{get_icon('search')} Search OCR Index",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        )
        title.pack(pady=(0, SPACING["large"]))

        desc = tk.Label(
            self,
            text="Search indexed OCR text and preview matching snippets",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
        )
        desc.pack(pady=(0, SPACING["medium"]))

        query_frame = tk.LabelFrame(
            self,
            text="Search Parameters",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["medium"],
        )
        query_frame.pack(fill=tk.X, pady=SPACING["medium"])

        keyword_row = tk.Frame(query_frame, bg=COLORS["bg_secondary"])
        keyword_row.pack(fill=tk.X, pady=(0, SPACING["small"]))

        tk.Label(
            keyword_row,
            text="Keyword:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=10,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        keyword_entry = tk.Entry(
            keyword_row,
            textvariable=self.keyword_var,
            font=FONTS["default"],
            bg="white",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        keyword_entry.bind("<Return>", lambda _evt: self._start_search())

        options_row = tk.Frame(query_frame, bg=COLORS["bg_secondary"])
        options_row.pack(fill=tk.X, pady=SPACING["small"])

        tk.Label(
            options_row,
            text="Limit:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=10,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        limit_spin = tk.Spinbox(
            options_row,
            from_=1,
            to=200,
            textvariable=self.limit_var,
            font=FONTS["default"],
            width=5,
        )
        limit_spin.pack(side=tk.LEFT, padx=(0, SPACING["medium"]))

        tk.Label(
            options_row,
            text="Context:",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            width=10,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        context_spin = tk.Spinbox(
            options_row,
            from_=20,
            to=200,
            increment=10,
            textvariable=self.context_var,
            font=FONTS["default"],
            width=5,
        )
        context_spin.pack(side=tk.LEFT)

        action_frame = tk.Frame(query_frame, bg=COLORS["bg_secondary"])
        action_frame.pack(fill=tk.X, pady=(SPACING["small"], 0))

        self.search_btn = tk.Button(
            action_frame,
            text=f"{get_icon('search')} Search",
            command=self._start_search,
            bg=COLORS["accent"],
            fg="white",
            font=FONTS["button"],
            padx=24,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
        )
        self.search_btn.pack(side=tk.RIGHT)

        results_frame = tk.LabelFrame(
            self,
            text="Results",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
            padx=SPACING["medium"],
            pady=SPACING["small"],
        )
        results_frame.pack(fill=tk.BOTH, expand=True)

        tree_container = tk.Frame(results_frame, bg=COLORS["bg_secondary"])
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("file", "page", "snippet")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=10,
        )
        self.tree.heading("file", text="File")
        self.tree.heading("page", text="Page")
        self.tree.heading("snippet", text="Snippet")
        self.tree.column("file", width=220, anchor=tk.W)
        self.tree.column("page", width=60, anchor=tk.CENTER)
        self.tree.column("snippet", width=460, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        status_label = tk.Label(
            self,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
        )
        status_label.pack(fill=tk.X, pady=(SPACING["small"], 0))

    # ------------------------------------------------------------------
    def _start_search(self) -> None:
        keyword = self.keyword_var.get().strip()
        if not keyword:
            show_error("Missing keyword", "請輸入要搜尋的關鍵字。")
            return

        if self.worker and self.worker.is_alive():
            return

        self.search_btn.config(state=tk.DISABLED)
        self.status_var.set("Searching...")
        self.main_window.show_message("Searching OCR index", "info")

        params = {
            "keyword": keyword,
            "limit": int(self.limit_var.get()),
            "context": int(self.context_var.get()),
        }

        self.worker = threading.Thread(target=self._run_search, args=(params,), daemon=True)
        self.worker.start()

    def _run_search(self, params: dict) -> None:
        try:
            results = self.extractor.search_keyword(
                params["keyword"],
                limit=params["limit"],
                context_chars=params["context"],
            )
        except Exception as exc:  # pragma: no cover - runtime feedback
            self.after(0, lambda: self._on_search_error(str(exc)))
        else:
            self.after(0, lambda: self._on_search_complete(params["keyword"], results))

    def _on_search_complete(self, keyword: str, results) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_results = [
            {
                "file_path": str(result.file_path),
                "page": result.page,
                "snippet": result.snippet,
            }
            for result in results
        ]

        if not results:
            self.status_var.set(f"No results for '{keyword}'")
            show_info("無結果", "找不到匹配的內容。")
            self.search_btn.config(state=tk.NORMAL)
            self.main_window.show_message("No matches found", "warning")
            return

        for idx, result in enumerate(results):
            self.tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(result.file_path.name, result.page, result.snippet),
            )

        self.status_var.set(f"Found {len(results)} results for '{keyword}'")
        self.search_btn.config(state=tk.NORMAL)
        self.main_window.show_message("Search complete", "success")

    def _on_search_error(self, message: str) -> None:
        self.search_btn.config(state=tk.NORMAL)
        self.status_var.set("Search failed")
        self.main_window.show_message("Search failed", "error")
        show_error("搜尋失敗", message)

    def _on_select(self, _event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        index = int(selection[0])
        if index >= len(self.current_results):
            return

        result = self.current_results[index]
        file_path = result.get("file_path", "")
        snippet = result.get("snippet", "")
        self.status_var.set(f"{file_path} :: {snippet[:80]}...")
