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
- ✅ Basic compression using pikepdf with linearization support
- ✅ Query PDF file information and metadata
- ✅ Graphical User Interface (GUI) for easy operation
- ✅ OCR extraction for scanned PDFs with searchable index support

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

# Aggressive compression flag (currently falls back to basic compression with reminder)
python pdf_toolkit.py optimize input.pdf -o optimized_aggressive.pdf --aggressive --dpi 150
```

#### View PDF Information
```bash
python pdf_toolkit.py info input.pdf
```

#### OCR Extract and Index
```bash
# Run OCR on all PDFs inside ./scans and build SQLite index
python pdf_toolkit.py ocr-extract --folder ./scans --lang chi_tra+eng

# Include subdirectories and force re-indexing
python pdf_toolkit.py ocr-extract --folder ./archive --recursive --force
```

#### Search OCR Index
```bash
# Search for keyword across indexed OCR text
python pdf_toolkit.py search-text --keyword "報價單"

# Output results as JSON with more context
python pdf_toolkit.py search-text --keyword "Invoice" --context 120 --json
```

#### Export OCR Index
```bash
python pdf_toolkit.py ocr-export --output ./data/index_export.json
```

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
- **OCR Extract**: Batch OCR scanned PDFs and build a searchable index
- **Search**: Query OCR results directly from the built-in index

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
- pytesseract (requires Tesseract OCR runtime)
- ocrmypdf (optional alternative OCR engine)
- sqlite-utils

### GUI Requirements (Optional)
- tkinter (usually included with Python)


## Author

Taki HOR

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


