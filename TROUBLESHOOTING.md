# Troubleshooting Guide

## Static Directory Error

### Problem
If you encounter an error like:
```
RuntimeError: Directory 'static/' does not exist
```

This is caused by a conflicting `frontend` package in your virtual environment that has nothing to do with PDF processing.

### Root Cause
When `fitz` (PyMuPDF) is imported, a conflicting `frontend` package is being loaded. This package tries to mount a static files directory that doesn't exist in this project.

### Quick Fix
A `static/` directory has been created in the project root to satisfy this requirement. The directory is ignored by git (except for the README).

### Proper Solution
To completely resolve this issue, clean up your virtual environment:

1. **Deactivate and remove the old venv:**
   ```bash
   deactivate
   rm -rf venv
   ```

2. **Create a fresh virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install only the required packages:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify the installation:**
   ```bash
   pip list | grep -i pymupdf
   # Should show: PyMuPDF and PyMuPDFb

   pip list | grep -i frontend
   # Should show nothing (no frontend package)
   ```

### Prevention
- Always use a clean virtual environment for each project
- Only install packages from `requirements.txt`
- Avoid installing unrelated packages in the project venv

## Other Common Issues

### Import Errors
If you get import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Permission Errors
If you get permission errors with pip cache:
```bash
pip install --no-cache-dir -r requirements.txt
```

### GUI Not Starting
Ensure you have tkinter installed (usually comes with Python):
```bash
sudo apt-get install python3-tk  # On Ubuntu/Debian
```
