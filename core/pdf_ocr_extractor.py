"""OCR extraction and search index management for PDF Toolkit."""

from __future__ import annotations

import hashlib
import io
import json
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

try:  # pragma: no cover - optional dependency
    import fitz  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled at runtime
    fitz = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import pytesseract  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled at runtime
    pytesseract = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from PIL import Image  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled at runtime
    Image = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import ocrmypdf  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled at runtime
    ocrmypdf = None  # type: ignore[assignment]

ProgressCallback = Callable[[int, int, Path, str, str], None]
"""Signature for progress callback used during batch OCR.

The callback receives the current index (1-based), total count, the PDF path,
status string (``"start"``, ``"success"``, ``"skip"``, ``"error"``) and an
informational message.
"""


@dataclass(slots=True)
class SearchResult:
    """Represents a matched record from the OCR search index."""

    file_path: Path
    page: int
    snippet: str
    keyword: str
    score: float


class PDFOCRExtractor:
    """OCR text extractor and SQLite index manager."""

    DEFAULT_LANG = "chi_tra+eng"

    def __init__(
        self,
        db_path: str | Path = "core/db/pdf_index.db",
        cache_dir: str | Path = "data/ocr_cache",
        log_path: str | Path = "data/logs/ocr_log.txt",
    ) -> None:
        self.db_path = Path(db_path)
        self.cache_dir = Path(cache_dir)
        self.log_path = Path(log_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self._ensure_db()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def ocr_single_pdf(
        self,
        pdf_path: str | Path,
        *,
        lang: str | None = None,
        dpi: int = 300,
        use_cache: bool = True,
        use_ocrmypdf: bool = False,
    ) -> tuple[str, int]:
        """Run OCR on a single PDF file and return extracted text."""

        path = Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(f"找不到 PDF 檔案：{path}")

        language = lang or self.DEFAULT_LANG
        self._ensure_dependencies(require_ocr=True)

        cache_entry = self._load_cache(path) if use_cache else None
        if cache_entry:
            text, page_count = cache_entry
            return text, page_count

        if use_ocrmypdf:
            text, page_count = self._ocr_via_ocrmypdf(path, language)
        else:
            text, page_count = self._ocr_via_pytesseract(path, language, dpi)

        if use_cache:
            self._store_cache(path, text, page_count, language, dpi, use_ocrmypdf)

        return text, page_count

    def index_pdf(
        self,
        pdf_path: str | Path,
        text: str,
        page_count: int,
        *,
        lang: str | None = None,
    ) -> str:
        """Insert or update OCR text in the SQLite index."""

        path = Path(pdf_path)
        language = lang or self.DEFAULT_LANG
        modified_ns = path.stat().st_mtime_ns if path.exists() else None

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            existing = conn.execute(
                "SELECT id, file_modified_at FROM pdf_index WHERE file_path = ?",
                (str(path),),
            ).fetchone()

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action = "updated" if existing else "inserted"

            conn.execute(
                """
                INSERT INTO pdf_index (
                    file_path, text_content, page_count, created_at,
                    file_modified_at, lang
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    text_content = excluded.text_content,
                    page_count = excluded.page_count,
                    created_at = excluded.created_at,
                    file_modified_at = excluded.file_modified_at,
                    lang = excluded.lang
                """,
                (
                    str(path),
                    text[:500_000],
                    page_count,
                    created_at,
                    modified_ns,
                    language,
                ),
            )

        self._log(f"索引更新：{path} ({action})")
        return action

    def batch_ocr_folder(
        self,
        folder: str | Path,
        *,
        lang: str | None = None,
        dpi: int = 300,
        recursive: bool = False,
        force: bool = False,
        use_cache: bool = True,
        use_ocrmypdf: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> dict:
        """Run OCR on all PDFs within a folder."""

        folder_path = Path(folder)
        if not folder_path.is_dir():
            raise FileNotFoundError(f"找不到資料夾：{folder_path}")

        language = lang or self.DEFAULT_LANG
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = sorted(folder_path.glob(pattern))
        total = len(pdf_files)

        stats = {
            "folder": str(folder_path),
            "total": total,
            "indexed": 0,
            "skipped": 0,
            "updated": 0,
            "errors": [],
            "duration": 0.0,
        }

        start_time = time.perf_counter()
        for index, pdf_file in enumerate(pdf_files, start=1):
            if progress_callback:
                progress_callback(index, total, pdf_file, "start", "開始處理")

            try:
                existing = None if force else self._get_index_record(pdf_file)
                needs_ocr = force or self._needs_reindex(pdf_file, existing)

                if not needs_ocr:
                    stats["skipped"] += 1
                    if progress_callback:
                        progress_callback(index, total, pdf_file, "skip", "已於索引中，略過")
                    continue

                text, page_count = self.ocr_single_pdf(
                    pdf_file,
                    lang=language,
                    dpi=dpi,
                    use_cache=use_cache,
                    use_ocrmypdf=use_ocrmypdf,
                )

                action = self.index_pdf(
                    pdf_file,
                    text,
                    page_count,
                    lang=language,
                )
                stats["indexed"] += 1
                if action == "updated":
                    stats["updated"] += 1

                if progress_callback:
                    progress_callback(index, total, pdf_file, "success", "OCR 完成")
            except Exception as exc:  # pragma: no cover - runtime error handling
                stats["errors"].append({"file": str(pdf_file), "error": str(exc)})
                self._log(f"處理失敗：{pdf_file} -> {exc}")
                if progress_callback:
                    progress_callback(index, total, pdf_file, "error", str(exc))

        stats["duration"] = time.perf_counter() - start_time
        return stats

    def search_keyword(
        self,
        keyword: str,
        *,
        limit: int = 20,
        context_chars: int = 80,
    ) -> list[SearchResult]:
        """Search the OCR index for a keyword and return contextual snippets."""

        sanitized = keyword.strip()
        if not sanitized:
            return []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT file_path, text_content
                FROM pdf_index
                WHERE text_content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{sanitized}%", limit),
            ).fetchall()

        results: list[SearchResult] = []
        for row in rows:
            text: str = row["text_content"] or ""
            file_path = Path(row["file_path"])

            position = text.lower().find(sanitized.lower())
            if position == -1:
                continue

            snippet = self._build_snippet(text, position, len(sanitized), context_chars)
            page = self._infer_page_number(text, position)
            results.append(
                SearchResult(
                    file_path=file_path,
                    page=page,
                    snippet=snippet,
                    keyword=sanitized,
                    score=1.0,
                )
            )

        return results

    def export_index(self, output_path: str | Path) -> Path:
        """Export the OCR index to a JSON file."""

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT file_path, text_content, page_count, created_at, lang FROM pdf_index"
            ).fetchall()

        payload = [dict(row) for row in rows]
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

        self._log(f"索引匯出：{out_path}")
        return out_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pdf_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    text_content TEXT,
                    page_count INTEGER,
                    created_at TEXT,
                    file_modified_at INTEGER,
                    lang TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pdf_file ON pdf_index(file_path)")

            existing_columns = {
                row[1]: row[2]
                for row in conn.execute("PRAGMA table_info(pdf_index)")
            }

            if "file_modified_at" not in existing_columns:
                conn.execute("ALTER TABLE pdf_index ADD COLUMN file_modified_at INTEGER")
            if "lang" not in existing_columns:
                conn.execute("ALTER TABLE pdf_index ADD COLUMN lang TEXT")

    def _ensure_dependencies(self, *, require_ocr: bool = False) -> None:
        if fitz is None:
            raise ImportError("PyMuPDF 未安裝，請先執行 'pip install PyMuPDF'。")
        if require_ocr and pytesseract is None:
            raise ImportError("pytesseract 未安裝，請先執行 'pip install pytesseract'。")
        if require_ocr and Image is None:
            raise ImportError("Pillow 未安裝，請先執行 'pip install Pillow'。")

    def _ocr_via_pytesseract(self, path: Path, language: str, dpi: int) -> tuple[str, int]:
        assert fitz is not None  # for type checkers
        assert pytesseract is not None
        assert Image is not None

        try:
            pytesseract.get_tesseract_version()
        except Exception as exc:  # pragma: no cover - runtime dependency check
            raise RuntimeError("無法偵測 tesseract 可執行檔，請確認已安裝。") from exc

        doc = fitz.open(path)
        try:
            output_parts: list[str] = []
            for page_index, page in enumerate(doc, start=1):
                pix = page.get_pixmap(dpi=dpi)
                img_bytes = pix.tobytes("png")
                with Image.open(io.BytesIO(img_bytes)) as image:
                    text = pytesseract.image_to_string(image, lang=language)
                clean_text = text.strip()
                output_parts.append(f"=== Page {page_index} ===\n{clean_text}\n")
            joined = "\n".join(output_parts)
            return joined, doc.page_count
        finally:
            doc.close()

    def _ocr_via_ocrmypdf(self, path: Path, language: str) -> tuple[str, int]:
        if ocrmypdf is None:
            raise ImportError("ocrmypdf 未安裝，請先執行 'pip install ocrmypdf'。")
        assert fitz is not None

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            ocrmypdf.ocr(
                str(path),
                str(tmp_path),
                language=language,
                deskew=True,
                clean=True,
                progress_bar=False,
            )

            doc = fitz.open(tmp_path)
            try:
                output_parts = []
                for page_index, page in enumerate(doc, start=1):
                    text = page.get_text("text")
                    clean_text = text.strip()
                    output_parts.append(f"=== Page {page_index} ===\n{clean_text}\n")
                joined = "\n".join(output_parts)
                return joined, doc.page_count
            finally:
                doc.close()
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:  # pragma: no cover - best effort cleanup
                pass

    def _get_index_record(self, pdf_path: Path) -> Optional[sqlite3.Row]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT * FROM pdf_index WHERE file_path = ?",
                (str(pdf_path),),
            ).fetchone()

    def _needs_reindex(self, pdf_path: Path, existing: Optional[sqlite3.Row]) -> bool:
        if existing is None:
            return True
        modified_ns = pdf_path.stat().st_mtime_ns
        stored_ns = existing["file_modified_at"] or 0
        try:
            stored_ns_int = int(stored_ns)
        except (TypeError, ValueError):  # pragma: no cover - corrupted data
            return True
        return modified_ns > stored_ns_int

    def _build_snippet(
        self, text: str, position: int, keyword_len: int, context_chars: int
    ) -> str:
        start = max(0, position - context_chars)
        end = min(len(text), position + keyword_len + context_chars)
        snippet = text[start:end].replace("\n", " ")
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{snippet}{suffix}"

    def _infer_page_number(self, text: str, position: int) -> int:
        marker = "=== Page "
        marker_pos = text.rfind(marker, 0, position)
        if marker_pos == -1:
            return 1
        end_marker = text.find("===", marker_pos + len(marker))
        if end_marker == -1:
            return 1
        number_str = text[marker_pos + len(marker):end_marker].strip()
        try:
            return int(number_str)
        except ValueError:  # pragma: no cover - unexpected format
            return 1

    def _cache_key(self, path: Path) -> str:
        key_source = f"{path.resolve()}::{path.stat().st_mtime_ns}"
        return hashlib.sha1(key_source.encode("utf-8")).hexdigest()

    def _cache_file(self, path: Path) -> Path:
        return self.cache_dir / f"{self._cache_key(path)}.json"

    def _load_cache(self, path: Path) -> Optional[tuple[str, int]]:
        cache_file = self._cache_file(path)
        if not cache_file.exists():
            return None
        try:
            with cache_file.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            return payload.get("text", ""), int(payload.get("page_count", 0))
        except Exception:  # pragma: no cover - cache corruption fallback
            return None

    def _store_cache(
        self,
        path: Path,
        text: str,
        page_count: int,
        language: str,
        dpi: int,
        use_ocrmypdf: bool,
    ) -> None:
        cache_file = self._cache_file(path)
        payload = {
            "text": text,
            "page_count": page_count,
            "lang": language,
            "dpi": dpi,
            "ocrmypdf": use_ocrmypdf,
            "cached_at": datetime.now().isoformat(),
        }
        with cache_file.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(f"[{timestamp}] {message}\n")
        except Exception:  # pragma: no cover - logging must not fail
            pass
