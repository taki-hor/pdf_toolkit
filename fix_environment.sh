#!/bin/bash
# =============================================================================
# Environment Fix Script for PDF Toolkit
# =============================================================================
# This script fixes the package conflict issue where a 'frontend' package
# interferes with PyMuPDF's fitz module.
#
# Issue: RuntimeError: Directory 'static/' does not exist
# Cause: Conflicting 'frontend' package in the virtual environment
# =============================================================================

set -e

echo "============================================"
echo "PDF Toolkit Environment Fix"
echo "============================================"
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ERROR: No virtual environment detected!"
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    echo ""
    exit 1
fi

echo "Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Check for the conflicting frontend package
if python -c "import frontend" 2>/dev/null; then
    echo "WARNING: Conflicting 'frontend' package found!"
    echo "This package interferes with PyMuPDF and must be removed."
    echo ""

    read -p "Do you want to uninstall the 'frontend' package? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Uninstalling 'frontend' package..."
        pip uninstall -y frontend || true
        echo "Done!"
        echo ""
    fi
fi

# Check if fitz can be imported correctly
echo "Checking PyMuPDF installation..."
if python -c "import sys; import fitz; sys.exit(0 if hasattr(fitz, 'Document') else 1)" 2>/dev/null; then
    echo "PyMuPDF is installed correctly!"
else
    echo "PyMuPDF is not installed correctly. Reinstalling..."
    pip uninstall -y PyMuPDF pymupdf-fonts 2>/dev/null || true
    pip install PyMuPDF>=1.23.0
    echo "Done!"
fi

echo ""
echo "Verifying installation..."
python -c "import fitz; print(f'PyMuPDF version: {fitz.version}')"

echo ""
echo "============================================"
echo "Environment fix completed successfully!"
echo "============================================"
