"""
Background worker thread for PDF operations.
"""

import threading
from typing import Callable, Optional, Dict, Any
import sys
import os

# Add parent directory to path to import pdf_toolkit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pdf_toolkit import (
    merge_pdfs, split_pdf, delete_pages,
    rotate_pages, add_watermark, optimize_pdf,
    get_pdf_info, ocr_pdf_to_text
)


class PDFWorker(threading.Thread):
    """
    Background worker thread for PDF operations.
    Runs PDF operations without blocking the GUI.
    """

    def __init__(
        self,
        operation: str,
        params: Dict[str, Any],
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
    ):
        """
        Initialize PDF worker.

        Args:
            operation: Operation name (merge, split, delete, rotate, watermark, optimize, info, ocr)
            params: Parameters for the operation
            on_complete: Callback function on successful completion
            on_error: Callback function on error
            on_progress: Callback function for progress updates (not implemented yet)
        """
        super().__init__(daemon=True)
        self.operation = operation
        self.params = params
        self.on_complete = on_complete
        self.on_error = on_error
        self.on_progress = on_progress
        self.result = None
        self.error = None

    def run(self) -> None:
        """Execute the PDF operation in background."""
        try:
            if self.operation == "merge":
                merge_pdfs(
                    self.params["input_pdfs"],
                    self.params["output_pdf"]
                )
                self.result = {"output": self.params["output_pdf"]}

            elif self.operation == "split":
                split_pdf(
                    self.params["input_pdf"],
                    self.params["output_dir"],
                    self.params.get("page_spec")
                )
                self.result = {"output_dir": self.params["output_dir"]}

            elif self.operation == "delete":
                delete_pages(
                    self.params["input_pdf"],
                    self.params["output_pdf"],
                    self.params["page_spec"]
                )
                self.result = {"output": self.params["output_pdf"]}

            elif self.operation == "rotate":
                rotate_pages(
                    self.params["input_pdf"],
                    self.params["output_pdf"],
                    self.params["page_spec"],
                    self.params["angle"]
                )
                self.result = {"output": self.params["output_pdf"]}

            elif self.operation == "watermark":
                add_watermark(
                    self.params["input_pdf"],
                    self.params["output_pdf"],
                    self.params["text"],
                    size=self.params.get("size", 36),
                    alpha=self.params.get("alpha", 0.3),
                    angle=self.params.get("angle", 0),
                    color=self.params.get("color", (0.5, 0.5, 0.5))
                )
                self.result = {"output": self.params["output_pdf"]}

            elif self.operation == "optimize":
                optimize_pdf(
                    self.params["input_pdf"],
                    self.params["output_pdf"],
                    linearize=self.params.get("linearize", False),
                    aggressive=self.params.get("aggressive", False),
                    dpi=self.params.get("dpi", 150),
                    quality_level=self.params.get("quality"),
                    remove_unused=self.params.get("remove_unused", True),
                    compress_images=self.params.get("compress_images", True),
                    remove_duplicates=self.params.get("remove_duplicates", True),
                    target_reduction=self.params.get("target_reduction"),
                )
                self.result = {"output": self.params["output_pdf"]}

            elif self.operation == "info":
                info = get_pdf_info(self.params["input_pdf"])
                self.result = info

            elif self.operation == "ocr":
                text = ocr_pdf_to_text(
                    self.params["input_pdf"],
                    output_docx=self.params.get("output_docx"),
                    output_odt=self.params.get("output_odt"),
                    output_txt=self.params.get("output_txt"),
                    language=self.params.get("language", "eng"),
                    dpi=self.params.get("dpi", 300),
                    progress_callback=self.on_progress
                )
                self.result = {
                    "text": text,
                    "outputs": {
                        "docx": self.params.get("output_docx"),
                        "odt": self.params.get("output_odt"),
                        "txt": self.params.get("output_txt")
                    }
                }

            else:
                raise ValueError(f"Unknown operation: {self.operation}")

            # Call completion callback if provided
            if self.on_complete:
                self.on_complete(self.result)

        except Exception as e:
            self.error = str(e)
            if self.on_error:
                self.on_error(self.error)
