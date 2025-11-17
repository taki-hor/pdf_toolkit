"""Command line interface for pdf_toolkit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click


def _load_data_dict(data_json: Optional[str], data_file: Optional[Path]) -> dict:
    """Return a dictionary parsed from JSON string or file."""
    if data_json:
        try:
            return json.loads(data_json)
        except json.JSONDecodeError as exc:
            raise click.ClickException(f"Invalid JSON provided via --data-json: {exc}") from exc

    if data_file:
        try:
            text = Path(data_file).read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise click.ClickException(f"Invalid JSON content in file '{data_file}': {exc}") from exc

    raise click.UsageError("Either --data-json or --data-file must be provided.")


@click.group()
def cli() -> None:
    """Toolkit with PDF automation utilities."""


@cli.command("fill-template")
@click.option(
    "template_path",
    "--template",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the DOCX or PDF template file.",
)
@click.option(
    "data_json",
    "--data-json",
    type=str,
    help="Inline JSON string with placeholder values (overrides --data-file).",
)
@click.option(
    "data_file",
    "--data-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to a JSON file containing placeholder values.",
)
def fill_template_command(template_path: Path, data_json: Optional[str], data_file: Optional[Path]) -> None:
    """Fill DOCX templates or interactive PDF forms using placeholder data."""
    data = _load_data_dict(data_json, data_file)
    suffix = template_path.suffix.lower()

    try:
        if suffix == ".docx":
            from core.template_filler import TemplateFiller

            filler = TemplateFiller()
            output_path = filler.fill_docx_template(template_path, data)
        elif suffix == ".pdf":
            from core.template_filler import TemplateFiller

            filler = TemplateFiller()
            output_path = filler.fill_pdf_form(template_path, data)
        else:
            raise click.ClickException("Unsupported template type. Use a .docx or .pdf file.")
    except ImportError as exc:  # pragma: no cover - runtime dependency issue
        missing = "python-docx" if "docx" in str(exc).lower() else "PyMuPDF"
        raise click.ClickException(
            f"Missing dependency '{missing}'. Please install it to use this feature."
        ) from exc
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Generated file: {output_path}")


@cli.command("pdf-diff")
@click.option(
    "old_pdf",
    "--old",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the original PDF file.",
)
@click.option(
    "new_pdf",
    "--new",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the updated PDF file.",
)
@click.option(
    "html_report",
    "--html-report",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Optional path to save an HTML comparison report.",
)
def pdf_diff_command(old_pdf: Path, new_pdf: Path, html_report: Optional[Path]) -> None:
    """Compare two PDFs and show line-level differences."""
    from core.pdf_diff_tool import PDFDiffTool

    tool = PDFDiffTool()
    try:
        result = tool.compare_pdfs(old_pdf, new_pdf)
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Similarity: {result.similarity:.2f}%")
    click.echo(f"Added lines: {len(result.added)}")
    click.echo(f"Deleted lines: {len(result.deleted)}")
    click.echo(f"Modified pairs: {len(result.modified)}")

    if result.key_changes:
        summary = ", ".join(sorted(result.key_changes.keys()))
        click.echo(f"Key changes detected for: {summary}")
    else:
        click.echo("Key changes detected for: none")

    if html_report:
        try:
            report_path = tool.generate_html_report(result, html_report)
        except OSError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(f"HTML report saved to: {report_path}")


@cli.command("ocr")
@click.option(
    "input_pdf",
    "--input",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the PDF file to perform OCR on.",
)
@click.option(
    "output_docx",
    "--docx",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for Microsoft Word (.docx) format.",
)
@click.option(
    "output_odt",
    "--odt",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for LibreOffice Writer (.odt) format.",
)
@click.option(
    "output_txt",
    "--txt",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for plain text (.txt) format.",
)
@click.option(
    "--language",
    default="eng",
    help="OCR language code (default: eng). Common codes: eng, chi_sim, chi_tra, fra, deu, spa, jpn.",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="DPI resolution for rendering pages (default: 300).",
)
def ocr_command(
    input_pdf: Path,
    output_docx: Optional[Path],
    output_odt: Optional[Path],
    output_txt: Optional[Path],
    language: str,
    dpi: int,
) -> None:
    """Extract text from PDF using OCR and save to Word, ODT, or text format."""
    if not output_docx and not output_odt and not output_txt:
        raise click.UsageError("At least one output format (--docx, --odt, or --txt) must be specified.")

    try:
        from pdf_toolkit import ocr_pdf_to_text

        ocr_pdf_to_text(
            str(input_pdf),
            output_docx=str(output_docx) if output_docx else None,
            output_odt=str(output_odt) if output_odt else None,
            output_txt=str(output_txt) if output_txt else None,
            language=language,
            dpi=dpi,
        )
    except ImportError as exc:
        missing_lib = "pytesseract" if "pytesseract" in str(exc).lower() else "odfpy" if "odf" in str(exc).lower() else "unknown"
        raise click.ClickException(
            f"Missing dependency '{missing_lib}'. Please install it to use OCR feature."
        ) from exc
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
