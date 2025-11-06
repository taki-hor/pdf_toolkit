"""
Sidebar navigation component for PDF Toolkit GUI.
"""

import tkinter as tk
from typing import Callable
from gui.utils.theme import COLORS, FONTS, WINDOW
from gui.utils.icons import get_icon


class Sidebar(tk.Frame):
    """
    Sidebar with navigation buttons for different PDF operations.
    """

    # Feature buttons configuration
    FEATURES = [
        ("merge", "Merge", "Merge multiple PDF files"),
        ("split", "Split", "Split PDF into multiple files"),
        ("info", "Info", "View PDF information"),
        None,  # Separator
        ("delete", "Delete", "Delete specific pages"),
        ("rotate", "Rotate", "Rotate page orientation"),
        ("watermark", "Watermark", "Add text watermark"),
        ("optimize", "Optimize", "Compress and optimize PDF"),
    ]

    def __init__(self, parent, on_feature_select: Callable[[str], None]):
        """
        Initialize sidebar.

        Args:
            parent: Parent widget
            on_feature_select: Callback when feature is selected (receives feature name)
        """
        super().__init__(
            parent,
            width=WINDOW["sidebar_width"],
            bg=COLORS["bg_sidebar"]
        )
        self.on_feature_select = on_feature_select
        self.active_feature = None
        self.buttons = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup sidebar UI."""
        # Logo/Title
        title_frame = tk.Frame(self, bg=COLORS["bg_sidebar"])
        title_frame.pack(fill=tk.X, pady=(20, 30))

        title_label = tk.Label(
            title_frame,
            text="PDF Toolkit",
            font=("Arial", 16, "bold"),
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_sidebar"]
        )
        title_label.pack()

        version_label = tk.Label(
            title_frame,
            text="v0.2.0",
            font=("Arial", 9),
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_secondary"]
        )
        version_label.pack()

        # Feature buttons
        for item in self.FEATURES:
            if item is None:
                # Separator
                separator = tk.Frame(self, height=1, bg=COLORS["border"])
                separator.pack(fill=tk.X, padx=10, pady=10)
            else:
                feature_id, name, tooltip = item
                self._create_feature_button(feature_id, name, tooltip)

        # Spacer to push bottom content down
        tk.Frame(self, bg=COLORS["bg_sidebar"]).pack(fill=tk.BOTH, expand=True)

        # Help button at bottom
        help_btn = tk.Button(
            self,
            text=f"{get_icon('help')} Help",
            command=self._show_help,
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_sidebar"],
            font=FONTS["sidebar"],
            relief=tk.FLAT,
            anchor=tk.W,
            padx=20,
            pady=12,
            cursor="hand2",
            borderwidth=0
        )
        help_btn.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10))

    def _create_feature_button(self, feature_id: str, name: str, tooltip: str) -> None:
        """
        Create a feature button.

        Args:
            feature_id: Feature identifier
            name: Display name
            tooltip: Tooltip text
        """
        # Get icon
        icon = get_icon(feature_id, "")

        btn = tk.Button(
            self,
            text=f"{icon} {name}",
            command=lambda: self._on_button_click(feature_id),
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_sidebar"],
            font=FONTS["sidebar"],
            relief=tk.FLAT,
            anchor=tk.W,
            padx=20,
            pady=15,
            cursor="hand2",
            borderwidth=0
        )
        btn.pack(fill=tk.X, padx=5, pady=2)

        # Store button reference
        self.buttons[feature_id] = btn

        # Hover effects
        btn.bind("<Enter>", lambda e: self._on_hover(feature_id, True))
        btn.bind("<Leave>", lambda e: self._on_hover(feature_id, False))

        # Store tooltip (for future implementation)
        btn.tooltip = tooltip

    def _on_button_click(self, feature_id: str) -> None:
        """
        Handle button click.

        Args:
            feature_id: Feature identifier
        """
        # Update active state
        if self.active_feature == feature_id:
            return  # Already active

        self._set_active_feature(feature_id)

        # Notify callback
        if self.on_feature_select:
            self.on_feature_select(feature_id)

    def _set_active_feature(self, feature_id: str) -> None:
        """
        Set active feature and update button states.

        Args:
            feature_id: Feature identifier
        """
        # Reset previous active button
        if self.active_feature and self.active_feature in self.buttons:
            self.buttons[self.active_feature].config(
                bg=COLORS["bg_sidebar"],
                relief=tk.FLAT
            )

        # Set new active button
        if feature_id in self.buttons:
            self.buttons[feature_id].config(
                bg=COLORS["button_hover"],
                relief=tk.FLAT
            )

        self.active_feature = feature_id

    def _on_hover(self, feature_id: str, entering: bool) -> None:
        """
        Handle button hover.

        Args:
            feature_id: Feature identifier
            entering: True if entering, False if leaving
        """
        if feature_id not in self.buttons:
            return

        btn = self.buttons[feature_id]

        # Don't change active button color
        if feature_id == self.active_feature:
            return

        if entering:
            btn.config(bg=COLORS["button_hover"])
        else:
            btn.config(bg=COLORS["bg_sidebar"])

    def _show_help(self) -> None:
        """Show help dialog."""
        # TODO: Implement help dialog
        from gui.utils.helpers import show_info
        show_info(
            "Help",
            "PDF Toolkit v0.2.0\n\n"
            "Select a feature from the left sidebar:\n"
            "- Merge - Combine multiple PDFs\n"
            "- Split - Split PDF pages\n"
            "- Info - View PDF information\n"
            "- Delete - Remove specific pages\n"
            "- Rotate - Rotate pages\n"
            "- Watermark - Add watermarks\n"
            "- Optimize - Compress file size\n"
            "- Author: Taki HOR\n\n"
            "GitHub: https://github.com/your-repo/pdf_toolkit"
        )
