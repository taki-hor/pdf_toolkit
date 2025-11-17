#!/usr/bin/env python3
"""
Environment Fix Script for PDF Toolkit
=======================================
This script fixes the package conflict issue where a 'frontend' package
interferes with PyMuPDF's fitz module.

Issue: RuntimeError: Directory 'static/' does not exist
Cause: Conflicting 'frontend' package in the virtual environment
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_virtual_env():
    """Check if we're running in a virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        print("ERROR: No virtual environment detected!")
        print("Please activate your virtual environment first:")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate    # Windows")
        return False

    print(f"Virtual environment detected: {sys.prefix}")
    return True


def check_frontend_package():
    """Check if the conflicting frontend package is installed."""
    try:
        import frontend  # noqa: F401
        return True
    except ImportError:
        return False


def uninstall_frontend():
    """Uninstall the conflicting frontend package."""
    print("Uninstalling 'frontend' package...")
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip uninstall -y frontend",
        check=False
    )
    if success or "not installed" in stderr.lower():
        print("Done!")
        return True
    else:
        print(f"Warning: {stderr}")
        return False


def verify_pymupdf():
    """Verify PyMuPDF is installed correctly."""
    try:
        import fitz
        if hasattr(fitz, 'Document'):
            print(f"PyMuPDF version: {fitz.version}")
            return True
        else:
            print("PyMuPDF is installed but appears corrupted.")
            return False
    except Exception as e:
        print(f"PyMuPDF import failed: {e}")
        return False


def reinstall_pymupdf():
    """Reinstall PyMuPDF cleanly."""
    print("Reinstalling PyMuPDF...")

    # Uninstall first
    print("  Uninstalling existing PyMuPDF...")
    run_command(
        f"{sys.executable} -m pip uninstall -y PyMuPDF pymupdf-fonts",
        check=False
    )

    # Install
    print("  Installing PyMuPDF>=1.23.0...")
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip install 'PyMuPDF>=1.23.0'"
    )

    if success:
        print("Done!")
        return True
    else:
        print(f"Error: {stderr}")
        return False


def main():
    """Main execution function."""
    print("=" * 44)
    print("PDF Toolkit Environment Fix")
    print("=" * 44)
    print()

    # Check virtual environment
    if not check_virtual_env():
        return 1

    print()

    # Check for conflicting frontend package
    has_frontend = check_frontend_package()

    if has_frontend:
        print("WARNING: Conflicting 'frontend' package found!")
        print("This package interferes with PyMuPDF and must be removed.")
        print()

        response = input("Do you want to uninstall the 'frontend' package? (y/n) ")
        print()

        if response.lower() in ('y', 'yes'):
            uninstall_frontend()
            print()

    # Check PyMuPDF installation
    print("Checking PyMuPDF installation...")

    if verify_pymupdf():
        print("PyMuPDF is installed correctly!")
    else:
        print("PyMuPDF is not installed correctly. Reinstalling...")
        if not reinstall_pymupdf():
            print()
            print("ERROR: Failed to reinstall PyMuPDF")
            return 1

    print()
    print("Verifying installation...")
    if not verify_pymupdf():
        print("ERROR: PyMuPDF verification failed after installation")
        return 1

    print()
    print("=" * 44)
    print("Environment fix completed successfully!")
    print("=" * 44)

    return 0


if __name__ == "__main__":
    sys.exit(main())
