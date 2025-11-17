# Static Directory

This directory exists as a workaround for a package conflict issue.

## Why This Exists

Some users may have a conflicting `frontend` package in their virtual environment that expects a `static/` directory to exist. This is not part of the PDF Toolkit application itself.

## Resolution

If you're experiencing issues related to this directory, please see `TROUBLESHOOTING.md` for instructions on how to properly clean up your virtual environment.

## Note

This directory should remain empty and is ignored by git. It's only here to prevent runtime errors during imports.
