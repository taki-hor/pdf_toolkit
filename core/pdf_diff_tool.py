"""PDF difference detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import difflib
import html
import importlib
import re

import fitz


@dataclass(slots=True)
class DiffResult:
    """Structured result for PDF comparisons."""

    added: List[str]
    deleted: List[str]
    modified: List[Tuple[str, str]]
    key_changes: Dict[str, List[str]]
    similarity: float


class PDFDiffTool:
    """Compare PDF documents and highlight textual differences."""

    def extract_text_with_structure(self, pdf_path: str | Path) -> Dict[str, object]:
        """Extract raw text and metadata from *pdf_path*."""
        path = Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF not found: {path}")

        result: Dict[str, object] = {
            "page_count": 0,
            "metadata": {},
            "pages": [],
            "full_text": "",
        }

        try:
            pdfplumber = importlib.import_module("pdfplumber")
        except ModuleNotFoundError:
            pdfplumber = None

        if pdfplumber is not None:
            with pdfplumber.open(str(path)) as pdf:
                result["page_count"] = len(pdf.pages)
                metadata = pdf.metadata or {}
                result["metadata"] = {
                    key: metadata.get(key)
                    for key in ("CreationDate", "ModDate", "Author", "Title")
                    if metadata.get(key) is not None
                }

                all_text: List[str] = []
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    lines = text.splitlines()
                    result["pages"].append(
                        {
                            "page_num": page_num,
                            "text": text,
                            "lines": lines,
                        }
                    )
                    all_text.append(text)
        else:
            with fitz.open(str(path)) as doc:
                result["page_count"] = doc.page_count
                metadata = doc.metadata or {}
                result["metadata"] = {
                    key: metadata.get(key)
                    for key in ("creationDate", "modDate", "author", "title")
                    if metadata.get(key) is not None
                }

                all_text = []
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text("text") or ""
                    lines = text.splitlines()
                    result["pages"].append(
                        {
                            "page_num": page_num,
                            "text": text,
                            "lines": lines,
                        }
                    )
                    all_text.append(text)

        result["full_text"] = "\n".join(all_text)
        return result

    def compare_pdfs(self, pdf1_path: str | Path, pdf2_path: str | Path) -> DiffResult:
        """Compare two PDFs and return a :class:`DiffResult`."""
        info1 = self.extract_text_with_structure(pdf1_path)
        info2 = self.extract_text_with_structure(pdf2_path)

        text1 = info1["full_text"] if isinstance(info1, dict) else ""
        text2 = info2["full_text"] if isinstance(info2, dict) else ""

        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        added_lines: List[str] = []
        deleted_lines: List[str] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                added_lines.extend(lines2[j1:j2])
            elif tag == "delete":
                deleted_lines.extend(lines1[i1:i2])
            elif tag == "replace":
                deleted_lines.extend(lines1[i1:i2])
                added_lines.extend(lines2[j1:j2])

        modified_pairs: List[Tuple[str, str]] = []
        remaining_deleted: List[str] = []
        used_added: set[int] = set()

        for old_line in deleted_lines:
            best_index: int | None = None
            best_ratio = 0.0
            for idx, new_line in enumerate(added_lines):
                if idx in used_added:
                    continue
                ratio = difflib.SequenceMatcher(None, old_line, new_line).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_index = idx
            if best_index is not None and best_ratio >= 0.6:
                modified_pairs.append((old_line, added_lines[best_index]))
                used_added.add(best_index)
            else:
                remaining_deleted.append(old_line)

        remaining_added = [line for idx, line in enumerate(added_lines) if idx not in used_added]

        key_changes = self._extract_key_changes(text1, text2)
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio() * 100

        return DiffResult(
            added=remaining_added,
            deleted=remaining_deleted,
            modified=modified_pairs,
            key_changes=key_changes,
            similarity=round(similarity, 2),
        )

    def _extract_key_changes(self, text1: str, text2: str) -> Dict[str, List[str]]:
        """Identify notable token differences (dates, amounts, ids, etc.)."""
        patterns: Dict[str, str] = {
            "dates": r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
            "currency": r"[\$€£]?\b\d{3,}(?:,\d{3})*(?:\.\d+)?\b",
            "percentages": r"\b\d+(?:\.\d+)?%\b",
            "ids": r"\b[A-Z]{2,}-?\d{2,}\b",
            "emails": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            "phones": r"\+?\d{1,3}(?:[\s().-]\d{3,}){2,}",
        }

        changes: Dict[str, List[str]] = {}
        for key, pattern in patterns.items():
            matches1 = set(re.findall(pattern, text1))
            matches2 = set(re.findall(pattern, text2))

            removed = sorted(matches1 - matches2)
            added = sorted(matches2 - matches1)

            if removed or added:
                entries: List[str] = []
                if removed:
                    entries.append("Removed: " + ", ".join(html.escape(item) for item in removed))
                if added:
                    entries.append("Added: " + ", ".join(html.escape(item) for item in added))
                changes[key] = entries

        return changes

    def generate_html_report(self, diff_result: DiffResult, output_path: str | Path) -> Path:
        """Create a human-friendly HTML report summarising *diff_result*."""
        path = Path(output_path)
        if path.is_dir():
            raise IsADirectoryError("Output path must be a file, not a directory")
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        def _format_lines(title: str, lines: List[str]) -> str:
            if not lines:
                return ""
            items = "".join(f"<li>{html.escape(line)}</li>" for line in lines)
            return f"<section><h3>{html.escape(title)}</h3><ul>{items}</ul></section>"

        modified_rows = "".join(
            "<tr><td>{old}</td><td>{new}</td></tr>".format(
                old=html.escape(old),
                new=html.escape(new),
            )
            for old, new in diff_result.modified
        )

        key_sections = "".join(
            "<section><h3>{key}</h3><ul>{items}</ul></section>".format(
                key=html.escape(key.title()),
                items="".join(f"<li>{entry}</li>" for entry in values),
            )
            for key, values in diff_result.key_changes.items()
        )

        html_content = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <title>PDF Diff Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; color: #333; margin: 0; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        section {{ background: #fff; border-radius: 8px; padding: 15px 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #3498db; color: #fff; }}
        ul {{ margin: 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>PDF Comparison Report</h1>
    <section>
        <p><strong>Similarity:</strong> {diff_result.similarity:.2f}%</p>
        <p><strong>Added lines:</strong> {len(diff_result.added)} | <strong>Deleted lines:</strong> {len(diff_result.deleted)} | <strong>Modified lines:</strong> {len(diff_result.modified)}</p>
    </section>
    {key_sections if key_sections else ""}
    {"" if not diff_result.modified else f"<section><h3>Modified Lines</h3><table><thead><tr><th>Original</th><th>New</th></tr></thead><tbody>{modified_rows}</tbody></table></section>"}
    {_format_lines("Added Lines", diff_result.added)}
    {_format_lines("Deleted Lines", diff_result.deleted)}
</body>
</html>
"""

        path.write_text(html_content, encoding="utf-8")
        return path

