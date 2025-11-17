# Troubleshooting Guide

## Common Issues and Solutions

### RuntimeError: Directory 'static/' does not exist

**Error Message:**
```
RuntimeError: Directory 'static/' does not exist
File "venv/lib/python3.8/site-packages/fitz/__init__.py", line 1, in <module>
    from frontend import *
```

**Cause:**
This error occurs when a conflicting Python package called `frontend` is installed in your virtual environment. This package interferes with PyMuPDF's `fitz` module and tries to access a non-existent `static/` directory during import.

**Solution:**

#### Option 1: Automated Fix (Recommended)

Run the provided fix script:

```bash
# Activate your virtual environment first
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Run the fix script
bash fix_environment.sh
```

#### Option 2: Manual Fix

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Check if the `frontend` package is installed:
   ```bash
   pip list | grep frontend
   ```

3. If found, uninstall it:
   ```bash
   pip uninstall frontend
   ```

4. Reinstall PyMuPDF to ensure it's clean:
   ```bash
   pip uninstall PyMuPDF
   pip install PyMuPDF>=1.23.0
   ```

5. Verify the installation:
   ```bash
   python -c "import fitz; print(fitz.version)"
   ```

#### Option 3: Quick Workaround (Temporary)

If you need a quick fix and can't modify the virtual environment, create the missing directory:

```bash
mkdir -p venv/lib/python3.8/site-packages/frontend/static
# Or for Python 3.9+, adjust the path accordingly
```

**Note:** This is only a workaround and doesn't fix the root cause. The proper solution is to remove the conflicting package.

### Prevention

To avoid this issue in the future:

1. Always use a clean virtual environment
2. Install dependencies from `requirements.txt` or `requirements-gui.txt`:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-gui.txt  # For GUI features
   ```
3. Avoid installing unrelated packages in the project's virtual environment
4. Use `pip list` periodically to check for unexpected packages

### Other Common Issues

#### Import Error: No module named 'fitz'

**Solution:**
```bash
pip install PyMuPDF>=1.23.0
```

#### GUI Doesn't Start

**Solution:**
Ensure GUI dependencies are installed:
```bash
pip install -r requirements-gui.txt
```

#### Permission Errors on Linux

**Solution:**
Make scripts executable:
```bash
chmod +x pdf_toolkit_gui.py
chmod +x fix_environment.sh
```

## Getting Help

If you encounter other issues not covered here, please:

1. Check the README.md for setup instructions
2. Verify your Python version (3.8+ required)
3. Ensure all dependencies are installed
4. Check the error message carefully for clues

For persistent issues, consider creating a fresh virtual environment and reinstalling all dependencies.
