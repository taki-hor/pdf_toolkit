"""Core functionality for pdf_toolkit."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = ["TemplateFiller", "SmartFiller", "PDFDiffTool", "DiffResult"]


def __getattr__(name: str) -> Any:
    """Provide lazy access to submodules to avoid heavy imports at startup."""
    if name in {"TemplateFiller", "SmartFiller"}:
        module = importlib.import_module(".template_filler", __name__)
        return getattr(module, name)
    if name in {"PDFDiffTool", "DiffResult"}:
        module = importlib.import_module(".pdf_diff_tool", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
