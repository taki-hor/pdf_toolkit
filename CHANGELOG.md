# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-11-15

### Added - CLI-GUI Feature Parity & Enhancements

#### 1. PDF Diff Tool (CLI Command)
- **New Command**: `pdf_toolkit.py diff`
- Compare two PDF files and identify textual differences
- Features:
  - Line-by-line comparison with added/deleted/modified detection
  - Smart detection of key changes (dates, currency, percentages, IDs, emails, phones)
  - Similarity percentage calculation
  - Two output modes:
    - `summary`: Terminal-friendly summary output
    - `html`: Full HTML report with styled diff visualization
- **Use Cases**:
  - Document revision tracking
  - Contract change detection
  - Quality assurance for document updates
  - Automated diff in CI/CD pipelines

**Example**:
```bash
# Terminal summary
python pdf_toolkit.py diff document_v1.pdf document_v2.pdf

# HTML report
python pdf_toolkit.py diff document_v1.pdf document_v2.pdf --format html -o report.html
```

#### 2. DOCX Template Filler (CLI Command)
- **New Command**: `pdf_toolkit.py template-fill`
- Fill DOCX templates containing `{{placeholder}}` syntax with data
- Features:
  - JSON file or command-line data input
  - Optional DOCX→PDF conversion via LibreOffice or docx2pdf
  - Preserves document formatting and structure
  - Handles split placeholders across XML runs
- **Use Cases**:
  - Automated document generation from templates
  - Batch processing of contracts, invoices, reports
  - CI/CD document workflows
  - Non-GUI template filling for scripts

**Example**:
```bash
# Fill DOCX template
python pdf_toolkit.py template-fill template.docx -o output.docx -v name="John Doe" -v date="2025-01-15"

# Fill and convert to PDF
python pdf_toolkit.py template-fill template.docx -o output.pdf -d data.json --to-pdf
```

#### 3. Metadata Editor (CLI Command)
- **New Command**: `pdf_toolkit.py edit-metadata`
- Edit PDF metadata (title, author, subject, keywords, creator, producer)
- Features:
  - JSON file or command-line key-value pairs
  - Preserves existing metadata not being updated
  - Supports all standard PDF metadata fields
- **Use Cases**:
  - Bulk metadata updates for document branding
  - Automated metadata standardization
  - Document organization and cataloging
  - Compliance and audit trail updates

**Example**:
```bash
# Update specific fields
python pdf_toolkit.py edit-metadata input.pdf -o output.pdf -v title="Annual Report" -v author="Acme Corp"

# Batch update from JSON
python pdf_toolkit.py edit-metadata input.pdf -o output.pdf -d metadata.json
```

#### 4. True Aggressive Optimization Mode
- **Enhanced Feature**: `pdf_toolkit.py optimize --aggressive`
- Removed placeholder warning - now delivers real compression
- Features:
  - Multi-pass image downsampling (up to 3 iterations)
  - Progressive quality reduction (JPEG quality 62→38)
  - Adaptive scaling (0.78→0.55 scale factor)
  - CMYK to RGB conversion for better compression
  - Lanczos resampling for quality preservation
  - Target-based compression ratios
- **Performance**:
  - Typical 30-70% file size reduction
  - Configurable DPI targets
  - Smart iteration stopping when targets are met
- **Use Cases**:
  - Web-optimized PDF generation
  - Email-friendly document sizes
  - Storage cost reduction
  - Bandwidth optimization

**Example**:
```bash
# Aggressive optimization
python pdf_toolkit.py optimize large_document.pdf -o optimized.pdf --aggressive --dpi 150
```

#### 5. DOCX to PDF Conversion Engine
- **New Feature**: Automatic DOCX→PDF conversion
- Dual-engine support:
  - **Primary**: LibreOffice headless conversion
  - **Fallback**: docx2pdf Python package (Windows)
- Features:
  - Automatic engine detection and selection
  - Timeout protection (60s conversion limit)
  - Graceful degradation (keeps DOCX on failure)
  - Clean temporary file handling
- Integrated into `template-fill --to-pdf` workflow

### Changed
- Removed aggressive optimization placeholder warning
- Updated README with comprehensive new feature documentation
- Enhanced error messages for missing dependencies

### Technical Details

**New Functions Added**:
- `compare_pdfs()` - PDF difference detection with multi-format output
- `edit_pdf_metadata()` - Metadata editing with validation
- `fill_docx_template()` - DOCX template processing with optional PDF conversion
- `convert_docx_to_pdf()` - Multi-engine DOCX→PDF converter

**New CLI Subcommands**:
1. `diff` - PDF comparison tool
2. `template-fill` - DOCX template filler
3. `edit-metadata` - Metadata editor

**Enhanced Functions**:
- `optimize_pdf()` - Removed placeholder warning, now fully functional

### Dependencies

**Optional Dependencies Added**:
- **LibreOffice** (recommended for DOCX→PDF conversion)
- **docx2pdf** (alternative for Windows DOCX→PDF conversion)

### Migration Notes

For users upgrading from 0.2.0:
- `optimize --aggressive` now performs real compression (no breaking changes)
- All existing CLI commands remain unchanged
- New commands are additive only

### Future Enhancements

Potential additions for future releases:
- Preset library for reusable template data sets
- Enhanced image optimization with DPI-based downsampling controls
- XMP metadata support for extended metadata editing
- Batch processing modes for all operations
- Template validation and placeholder discovery

---

## [0.2.0] - Previous Release

### Features
- PDF merge, split, delete, rotate operations
- Text watermarking
- Basic optimization (pikepdf)
- PDF info retrieval
- Interactive PDF form filling
- GUI application
- CLI interface with 8 subcommands

---

## Format

This project follows [Semantic Versioning](https://semver.org/).

- **Major** version for incompatible API changes
- **Minor** version for backward-compatible functionality additions
- **Patch** version for backward-compatible bug fixes
