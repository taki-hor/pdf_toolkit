"""Template filling utilities for pdf_toolkit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import re
import zipfile
from xml.etree import ElementTree as ET

import fitz

_PLACEHOLDER_PATTERN = re.compile(r"{{\s*([^{}]+?)\s*}}")
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_NSMAP = {"w": _W_NS}


def _register_default_namespaces() -> None:
    """Register common namespaces to keep ElementTree output tidy."""

    ET.register_namespace("w", _W_NS)
    ET.register_namespace("mc", "http://schemas.openxmlformats.org/markup-compatibility/2006")
    ET.register_namespace("wp", "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing")
    ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
    ET.register_namespace("w14", "http://schemas.microsoft.com/office/word/2010/wordml")
    ET.register_namespace("wpg", "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup")
    ET.register_namespace("wpi", "http://schemas.microsoft.com/office/word/2010/wordprocessingInk")
    ET.register_namespace("wne", "http://schemas.microsoft.com/office/word/2006/wordml")
    ET.register_namespace("wps", "http://schemas.microsoft.com/office/word/2010/wordprocessingShape")


def _sanitize_name(name: str) -> str:
    """Return a filesystem-friendly version of *name*."""
    sanitized = re.sub(r"[^A-Za-z0-9_.-]", "_", name.strip())
    return sanitized or "document"


def _replace_placeholders(text: str, data: Dict[str, Any]) -> str:
    """Replace placeholders of the form ``{{field}}`` using *data*."""

    def _replacement(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        value = data.get(key)
        return "" if value is None else str(value)

    return _PLACEHOLDER_PATTERN.sub(_replacement, text)


def _replace_in_paragraph_element(paragraph: ET.Element, data: Dict[str, Any]) -> bool:
    """Replace placeholders in a paragraph element.

    The logic mirrors the python-docx implementation by concatenating all text
    runs, replacing placeholders, and collapsing the paragraph into a single
    run when changes occur.  This ensures split placeholders are handled while
    keeping the implementation dependency-free.
    """

    text_elements: List[ET.Element] = []
    texts: List[str] = []

    for run in paragraph.findall("w:r", _NSMAP):
        text = run.find("w:t", _NSMAP)
        if text is not None:
            text_elements.append(text)
            texts.append(text.text or "")

    if not text_elements:
        # Paragraphs can embed text in alternate structures (e.g. sdt).
        for text in paragraph.findall('.//w:t', _NSMAP):
            text_elements.append(text)
            texts.append(text.text or "")

    if not text_elements:
        return False

    original = "".join(texts)
    updated = _replace_placeholders(original, data)
    if updated == original:
        return False

    primary_text = text_elements[0]
    primary_text.text = updated
    primary_text.set(_XML_SPACE, "preserve")

    # Remove additional runs to collapse the paragraph into a single run.
    parent_runs = [run for run in list(paragraph) if run.tag == f"{{{_W_NS}}}r"]
    for run in parent_runs[1:]:
        paragraph.remove(run)

    # Clear any remaining text nodes that are not direct children.
    for extra in text_elements[1:]:
        extra.text = ""

    return True


def _replace_placeholders_in_document(xml_bytes: bytes, data: Dict[str, Any]) -> bytes:
    """Return updated ``word/document.xml`` content with placeholders filled."""

    _register_default_namespaces()

    root = ET.fromstring(xml_bytes)
    for paragraph in root.findall('.//w:p', _NSMAP):
        _replace_in_paragraph_element(paragraph, data)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


@dataclass(slots=True)
class TemplateFiller:
    """Fill DOCX or PDF templates using simple placeholder data."""

    templates_dir: Path = Path("templates")
    output_dir: Path = Path("output")
    data_dir: Path = Path("data")
    clients: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialise directories and load cached client data if available."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        clients_file = self.data_dir / "clients.json"
        if clients_file.is_file():
            try:
                self.clients = json.loads(clients_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.clients = {}
        else:
            self.clients = {}

    def fill_docx_template(self, template_path: str | Path, data: Dict[str, Any]) -> Path:
        """Fill a DOCX template with the provided *data* and return the output path."""
        path = Path(template_path)
        if not path.is_file():
            raise FileNotFoundError(f"Template not found: {path}")

        with zipfile.ZipFile(path, "r") as src:
            try:
                document_xml = src.read("word/document.xml")
            except KeyError as exc:  # pragma: no cover - corrupted files
                raise ValueError("The DOCX template is missing document.xml") from exc

            updated_xml = _replace_placeholders_in_document(document_xml, data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = str(data.get("client_name", "document"))
            filename = _sanitize_name(client_name)
            output_path = self.output_dir / f"{filename}_{timestamp}.docx"

            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as dest:
                for item in src.infolist():
                    if item.is_dir():
                        dest.writestr(item, b"")
                        continue
                    content = updated_xml if item.filename == "word/document.xml" else src.read(item.filename)
                    dest.writestr(item, content)

        return output_path

    def fill_pdf_form(self, template_path: str | Path, data: Dict[str, Any]) -> Path:
        """Fill an interactive PDF form using PyMuPDF and return the output path."""
        path = Path(template_path)
        if not path.is_file():
            raise FileNotFoundError(f"Template not found: {path}")

        doc = fitz.open(str(path))
        has_widgets = False

        try:
            for page in doc:
                raw_widgets = page.widgets()
                widgets = list(raw_widgets or [])
                if not widgets:
                    continue
                has_widgets = True
                for widget in widgets:
                    field_name = getattr(widget, "field_name", None)
                    if not field_name:
                        continue
                    if field_name in data:
                        widget.field_value = str(data[field_name])
                        widget.update()

            if not has_widgets:
                raise ValueError("No form fields detected in PDF form.")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"filled_{timestamp}.pdf"
            doc.save(str(output_path))
            return output_path
        finally:
            doc.close()

    def create_smart_template_config(self, template_name: str, fields: List[Dict[str, Any]]) -> Path:
        """Create a JSON configuration for a smart template definition."""
        config_dir = self.templates_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_path = config_dir / f"{_sanitize_name(template_name)}.json"
        config_path.write_text(json.dumps(fields, indent=2), encoding="utf-8")
        return config_path


class SmartFiller:
    """Helper utilities for smarter template suggestions."""

    @staticmethod
    def auto_detect_placeholders_from_docx(template_path: Path) -> List[str]:
        """Return a list of placeholder names detected in the given DOCX template."""
        path = Path(template_path)
        if not path.is_file():
            raise FileNotFoundError(f"Template not found: {path}")

        with zipfile.ZipFile(path, "r") as src:
            try:
                document_xml = src.read("word/document.xml")
            except KeyError as exc:  # pragma: no cover - corrupted files
                raise ValueError("The DOCX template is missing document.xml") from exc

        root = ET.fromstring(document_xml)

        placeholders = set()
        for paragraph in root.findall('.//w:p', _NSMAP):
            text_parts = [text.text or "" for text in paragraph.findall('.//w:t', _NSMAP)]
            if not text_parts:
                continue
            joined = "".join(text_parts)
            for match in _PLACEHOLDER_PATTERN.findall(joined):
                placeholders.add(match.strip())

        return sorted(placeholders)

    @staticmethod
    def suggest_default_value(field_name: str) -> Optional[str]:
        """Suggest a default value based on common placeholder naming patterns."""
        lowered = field_name.lower().strip()
        today = datetime.now()

        if lowered in {"today", "current_date"} or "date" in lowered:
            return today.strftime("%Y-%m-%d")
        if "time" in lowered:
            return today.strftime("%H:%M")
        if "name" in lowered:
            return "John Doe"
        if "email" in lowered:
            return "john.doe@example.com"
        if "phone" in lowered or "mobile" in lowered:
            return "+1-555-0100"
        if "address" in lowered:
            return "123 Main Street"
        if "amount" in lowered or "total" in lowered:
            return "1000"

        return None

