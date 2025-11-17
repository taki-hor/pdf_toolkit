# PDF Toolkit

Basic PDF editing features — merge, split, delete, rotate etc.

## GUI Preview

<img src="pictures/gui.png" alt="PDF Toolkit GUI" width="450">

## Features
- ✅ Merge multiple PDF files
- ✅ Split PDF (single pages or specified ranges)
- ✅ Delete specific pages (reverse deletion to avoid index misalignment)
- ✅ Rotate pages with cumulative angle support
- ✅ Add custom text watermarks to all pages
- ✅ Advanced compression with aggressive image optimization
- ✅ Query PDF file information and metadata
- ✅ **NEW** Edit PDF metadata (title, author, subject, keywords, etc.)
- ✅ **NEW** Compare two PDFs and generate diff reports (HTML or summary)
- ✅ **NEW** Fill DOCX templates with data and convert to PDF
- ✅ Autofill interactive PDF forms from JSON or inline data
- ✅ **NEW** OCR text extraction from scanned PDFs with multi-format export (DOCX, ODT, TXT)
- ✅ Graphical User Interface (GUI) for easy operation

## Installation

### Basic Installation (CLI only)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### GUI Installation (Optional)
```bash
pip install -r requirements-gui.txt
```

## Usage

### Command Line Interface (CLI)

All commands are invoked via `python pdf_toolkit.py <subcommand> [...]`. Use `-h` or `--help` to view complete documentation.

#### Merge PDFs
```bash
python pdf_toolkit.py merge input1.pdf input2.pdf input3.pdf -o merged.pdf
```

#### Split PDF
```bash
# Split into single pages
python pdf_toolkit.py split input.pdf -d output_folder/

# Split by range
python pdf_toolkit.py split input.pdf -d output_folder/ -p "1-10,21-30"
```

#### Delete Pages
```bash
python pdf_toolkit.py delete input.pdf -p "1,3,5-8" -o trimmed.pdf
```

#### Rotate Pages
```bash
python pdf_toolkit.py rotate input.pdf -p "1-5" -a 90 -o rotated.pdf
```

#### Add Text Watermark
```bash
python pdf_toolkit.py watermark input.pdf -t "CONFIDENTIAL" -o watermarked.pdf

# Custom parameters
python pdf_toolkit.py watermark input.pdf -t "DRAFT" --size 48 --alpha 0.2 --angle 30 -o draft.pdf
```

#### Compress and Optimize
```bash
# Basic compression (with optional linearization)
python pdf_toolkit.py optimize input.pdf -o optimized.pdf --linearize

# Aggressive compression with image recompression (true aggressive mode)
python pdf_toolkit.py optimize input.pdf -o optimized_aggressive.pdf --aggressive --dpi 150
```

#### View PDF Information
```bash
python pdf_toolkit.py info input.pdf
```

#### Edit PDF Metadata
```bash
# Edit metadata using command-line arguments
python pdf_toolkit.py edit-metadata input.pdf -o output.pdf -v title="My Document" -v author="John Doe"

# Edit metadata using JSON file
python pdf_toolkit.py edit-metadata input.pdf -o output.pdf -d metadata.json

# Supported metadata fields: title, author, subject, keywords, creator, producer
```

#### Compare Two PDFs (Diff)
```bash
# Show summary in terminal
python pdf_toolkit.py diff document_v1.pdf document_v2.pdf

# Generate HTML report
python pdf_toolkit.py diff document_v1.pdf document_v2.pdf --format html -o diff_report.html

# The diff tool detects:
# - Added/deleted/modified lines
# - Changes in dates, currency, percentages, IDs, emails, phone numbers
# - Similarity percentage
```

#### Fill DOCX Templates
```bash
# Fill a DOCX template with placeholders like {{name}}, {{date}}, etc.
python pdf_toolkit.py template-fill template.docx -o output.docx -v name="John Doe" -v date="2025-01-15"

# Fill from JSON data file
python pdf_toolkit.py template-fill template.docx -o output.docx -d data.json

# Fill and convert to PDF (requires LibreOffice or docx2pdf)
python pdf_toolkit.py template-fill template.docx -o output.pdf -d data.json --to-pdf
```

#### Autofill PDF Form Fields
```bash
# Inspect available form fields
python pdf_toolkit.py autofill form.pdf --list-fields

# Fill fields using a JSON payload (keys must match field names)
python pdf_toolkit.py autofill form.pdf -d data.json -o filled.pdf

# Override / add individual values on the command line
python pdf_toolkit.py autofill form.pdf -d data.json -v employee_id=EMP-001 -o filled.pdf

# Fill and flatten the result into static text
python pdf_toolkit.py autofill form.pdf -d data.json -o filled_flat.pdf --flatten
```

#### OCR Text Extraction
```bash
# Extract text from scanned PDF and save to Microsoft Word format
python pdf_toolkit.py ocr input.pdf --docx output.docx

# Extract text and save to LibreOffice Writer format
python pdf_toolkit.py ocr input.pdf --odt output.odt

# Extract text and save to plain text format
python pdf_toolkit.py ocr input.pdf --txt output.txt

# Save to multiple formats at once
python pdf_toolkit.py ocr input.pdf --docx output.docx --odt output.odt --txt output.txt

# Specify OCR language (for non-English documents)
python pdf_toolkit.py ocr input.pdf --docx output.docx --language chi_sim  # Simplified Chinese
python pdf_toolkit.py ocr input.pdf --docx output.docx --language fra      # French

# Adjust DPI for better quality (higher = better quality but slower)
python pdf_toolkit.py ocr input.pdf --docx output.docx --dpi 400
```

**Note**: OCR requires Tesseract to be installed on your system:
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

For additional language support, install language packs:
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr-chi-sim` (for Chinese)
- **macOS**: `brew install tesseract-lang`

### Graphical User Interface (GUI)

Launch the GUI application:
```bash
python pdf_toolkit_gui.py
```

The GUI provides an intuitive interface for all PDF operations:
- **Merge**: Combine multiple PDFs with drag-and-drop support
- **Split**: Split PDFs into individual pages or ranges
- **Info**: View detailed PDF metadata
- **Delete**: Remove specific pages
- **Rotate**: Rotate pages by 90, 180, or 270 degrees
- **Watermark**: Add customizable text watermarks
- **Optimize**: Compress PDFs with quality settings

## Page Number Syntax

- `1,3,5`: Individual pages
- `1-5`: Consecutive range
- `10-`: From page 10 to the end
- `1-3,5-7,10-`: Mixed usage

All page numbers are 1-based; the tool automatically removes duplicates and sorts them.

## Quick Validation (Optional)

The project includes `quick_test.py` for batch validation of all features (requires test PDFs):
```bash
python quick_test.py
```

## System Requirements

### Core Requirements
- Python 3.8+
- PyMuPDF (fitz)
- pikepdf
- Pillow
- tqdm

### GUI Requirements (Optional)
- tkinter (usually included with Python)

### DOCX to PDF Conversion (Optional)
For converting DOCX templates to PDF, install one of:
- **LibreOffice** (recommended): Install via your package manager
  - Ubuntu/Debian: `sudo apt install libreoffice`
  - macOS: `brew install libreoffice`
  - Windows: Download from https://www.libreoffice.org/
- **docx2pdf** (Python package): `pip install docx2pdf` (Windows only)

### OCR Requirements (Optional)
For OCR text extraction from scanned PDFs:
- **Tesseract OCR**: System-level installation required
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **pytesseract** (Python wrapper): Included in requirements.txt
- **python-docx**: For DOCX export (included in requirements.txt)
- **odfpy**: For ODT export (optional, may need manual installation: `pip install odfpy`)

## Author

Taki HOR

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


