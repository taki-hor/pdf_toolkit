"""
Icon resources for PDF Toolkit GUI.
Using Unicode emoji for cross-platform compatibility.
"""

ICONS = {
    # Main features - Using safe ASCII/basic symbols
    "merge": ">>",
    "split": "><",
    "delete": "X",
    "rotate": "@",
    "watermark": "(C)",
    "optimize": "*",
    "info": "i",

    # Actions
    "file": "*",
    "folder": "@",
    "add": "+",
    "remove": "-",
    "up": "^",
    "down": "v",
    "left": "<",
    "right": ">",
    "close": "X",
    "minimize": "-",
    "maximize": "[]",

    # Status
    "success": "OK",
    "error": "X",
    "warning": "!",
    "info_status": "i",
    "processing": "...",
    "ready": "*",

    # Tools
    "settings": "@",
    "help": "?",
    "preview": "o",
    "refresh": "@",
    "save": "v",
    "open": "o",

    # Misc
    "rocket": ">>",
    "checkmark": "OK",
    "cross": "X",
}

def get_icon(name: str, fallback: str = "") -> str:
    """
    Get icon by name with optional fallback.

    Args:
        name: Icon name from ICONS dictionary
        fallback: Fallback text if icon not found

    Returns:
        Icon string or fallback
    """
    return ICONS.get(name, fallback)
