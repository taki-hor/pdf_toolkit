"""
Main window for PDF Toolkit GUI.
"""

import tkinter as tk
from tkinter import ttk
from gui.sidebar import Sidebar
from gui.utils.theme import COLORS, FONTS, WINDOW, SPACING
from gui.utils.icons import get_icon


class MainWindow(tk.Tk):
    """
    Main application window for PDF Toolkit.
    """

    def __init__(self):
        super().__init__()

        # Configure safe fonts (avoid emoji fonts that cause X11 errors)
        self._configure_safe_fonts()

        # Window configuration
        self.title("PDF Toolkit")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.minsize(WINDOW["min_width"], WINDOW["min_height"])
        self.configure(bg=COLORS["bg_primary"])

        # Application state
        self.current_mode = None
        self.current_dialog = None

        # Setup UI
        self._setup_ui()
        self._center_window()

    def _configure_safe_fonts(self) -> None:
        """Configure Tkinter to use safe fonts that avoid emoji rendering issues."""
        try:
            from tkinter import font as tkfont

            # Use DejaVu Sans - safe font without emoji
            safe_family = "DejaVu Sans"
            safe_mono = "DejaVu Sans Mono"

            # Configure default fonts to avoid emoji font selection
            try:
                default_font = tkfont.nametofont("TkDefaultFont")
                default_font.configure(family=safe_family, size=10)
            except:
                pass

            try:
                text_font = tkfont.nametofont("TkTextFont")
                text_font.configure(family=safe_family, size=10)
            except:
                pass

            try:
                fixed_font = tkfont.nametofont("TkFixedFont")
                fixed_font.configure(family=safe_mono, size=10)
            except:
                pass
        except Exception:
            # If font configuration fails, continue anyway
            pass

    def _setup_ui(self) -> None:
        """Setup main window UI."""
        # Main container
        self.main_container = tk.Frame(self, bg=COLORS["bg_primary"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = Sidebar(self.main_container, self._on_feature_select)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Workspace container
        workspace_container = tk.Frame(
            self.main_container,
            bg=COLORS["bg_primary"]
        )
        workspace_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Workspace (content area)
        self.workspace = tk.Frame(
            workspace_container,
            bg=COLORS["bg_secondary"],
            relief=tk.FLAT
        )
        self.workspace.pack(
            fill=tk.BOTH,
            expand=True,
            padx=SPACING["medium"],
            pady=SPACING["medium"]
        )

        # Status bar
        self.statusbar = tk.Label(
            self,
            text=f"{get_icon('ready')} Ready | Select a feature from the left sidebar",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
            font=("Arial", 9),
            padx=10,
            pady=5
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Show welcome screen
        self._show_welcome()

    def _show_welcome(self) -> None:
        """Show welcome screen in workspace."""
        self._clear_workspace()

        welcome_frame = tk.Frame(self.workspace, bg=COLORS["bg_secondary"])
        welcome_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Icon
        icon_label = tk.Label(
            welcome_frame,
            text="[PDF]",
            font=("Arial", 48, "bold"),
            bg=COLORS["bg_secondary"]
        )
        icon_label.pack(pady=(0, 20))

        # Title
        title_label = tk.Label(
            welcome_frame,
            text="PDF Toolkit",
            font=("Arial", 24, "bold"),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=10)

        # Description
        desc_label = tk.Label(
            welcome_frame,
            text="Select a feature from the left sidebar to start",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=5)

        # Features list
        features_frame = tk.Frame(welcome_frame, bg=COLORS["bg_secondary"])
        features_frame.pack(pady=20)

        features = [
            ("Merge", "Combine multiple PDF files"),
            ("Split", "Split PDF into multiple files"),
            ("Info", "View detailed PDF information"),
        ]

        for name, desc in features:
            feature_label = tk.Label(
                features_frame,
                text=f"- {name} - {desc}",
                font=("Arial", 10),
                bg=COLORS["bg_secondary"],
                fg=COLORS["text_secondary"],
                anchor=tk.W
            )
            feature_label.pack(anchor=tk.W, pady=2)

    def _on_feature_select(self, feature: str) -> None:
        """
        Handle feature selection from sidebar.

        Args:
            feature: Feature identifier (merge, split, info, etc.)
        """
        self.current_mode = feature
        self._update_workspace(feature)
        self._update_statusbar(feature)

    def _update_workspace(self, feature: str) -> None:
        """
        Update workspace based on selected feature.

        Args:
            feature: Feature identifier
        """
        self._clear_workspace()

        # Import and display appropriate dialog
        if feature == "merge":
            from gui.dialogs.merge_dialog import MergeDialog
            self.current_dialog = MergeDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "split":
            from gui.dialogs.split_dialog import SplitDialog
            self.current_dialog = SplitDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "info":
            from gui.dialogs.info_dialog import InfoDialog
            self.current_dialog = InfoDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "delete":
            from gui.dialogs.delete_dialog import DeleteDialog
            self.current_dialog = DeleteDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "rotate":
            from gui.dialogs.rotate_dialog import RotateDialog
            self.current_dialog = RotateDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "watermark":
            from gui.dialogs.watermark_dialog import WatermarkDialog
            self.current_dialog = WatermarkDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        elif feature == "optimize":
            from gui.dialogs.optimize_dialog import OptimizeDialog
            self.current_dialog = OptimizeDialog(self.workspace, self)
            self.current_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def _show_coming_soon(self, feature: str) -> None:
        """Show coming soon message for unimplemented features."""
        coming_soon_frame = tk.Frame(self.workspace, bg=COLORS["bg_secondary"])
        coming_soon_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        icon_label = tk.Label(
            coming_soon_frame,
            text="[WIP]",
            font=("Arial", 36, "bold"),
            bg=COLORS["bg_secondary"]
        )
        icon_label.pack(pady=(0, 20))

        title_label = tk.Label(
            coming_soon_frame,
            text="Coming Soon",
            font=("Arial", 20, "bold"),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            coming_soon_frame,
            text=f"'{feature}' feature will be available soon",
            font=FONTS["default"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        desc_label.pack(pady=5)

    def _clear_workspace(self) -> None:
        """Clear all widgets from workspace."""
        for widget in self.workspace.winfo_children():
            widget.destroy()
        self.current_dialog = None

    def _update_statusbar(self, feature: str) -> None:
        """
        Update status bar text based on current feature.

        Args:
            feature: Feature identifier
        """
        feature_names = {
            "merge": "Merge PDF",
            "split": "Split PDF",
            "delete": "Delete Pages",
            "rotate": "Rotate Pages",
            "watermark": "Add Watermark",
            "optimize": "Optimize PDF",
            "info": "PDF Info",
        }

        name = feature_names.get(feature, feature)
        self.statusbar.config(
            text=f"{get_icon('ready')} Current: {name}"
        )

    def _center_window(self) -> None:
        """Center window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_message(self, message: str, msg_type: str = "info") -> None:
        """
        Show message in status bar.

        Args:
            message: Message text
            msg_type: Message type (info, success, warning, error)
        """
        icons = {
            "info": get_icon("info_status"),
            "success": get_icon("success"),
            "warning": get_icon("warning"),
            "error": get_icon("error"),
        }

        colors = {
            "info": COLORS["text_secondary"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
        }

        icon = icons.get(msg_type, get_icon("info_status"))
        color = colors.get(msg_type, COLORS["text_secondary"])

        self.statusbar.config(
            text=f"{icon} {message}",
            fg=color
        )
