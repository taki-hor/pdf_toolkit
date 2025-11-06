"""
Theme configuration for PDF Toolkit GUI.
"""

# Color scheme
COLORS = {
    "bg_primary": "#F5F5F5",      # Main background - Light gray
    "bg_secondary": "#FFFFFF",    # Secondary background - White
    "bg_sidebar": "#2C3E50",      # Sidebar - Dark blue-gray
    "text_primary": "#2C3E50",    # Main text - Dark gray
    "text_secondary": "#7F8C8D",  # Secondary text - Gray
    "text_sidebar": "#ECF0F1",    # Sidebar text - Light gray-white
    "accent": "#3498DB",          # Accent color - Blue
    "accent_hover": "#2980B9",    # Accent hover - Darker blue
    "success": "#27AE60",         # Success - Green
    "warning": "#F39C12",         # Warning - Orange
    "error": "#E74C3C",           # Error - Red
    "border": "#BDC3C7",          # Border - Light gray
    "button_hover": "#3E5871",    # Button hover - Dark blue-gray
}

# Font configuration
FONTS = {
    "default": ("Arial", 10),
    "heading": ("Arial", 14, "bold"),
    "title": ("Arial", 16, "bold"),
    "button": ("Arial", 10),
    "sidebar": ("Arial", 11),
    "mono": ("Courier New", 10),
}

# Spacing
SPACING = {
    "small": 5,
    "medium": 10,
    "large": 20,
}

# Window dimensions
WINDOW = {
    "width": 1024,
    "height": 768,
    "min_width": 800,
    "min_height": 600,
    "sidebar_width": 200,
}
