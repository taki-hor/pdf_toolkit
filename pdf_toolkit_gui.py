#!/usr/bin/env python3
"""
PDF Toolkit GUI - Graphical User Interface
Entry point for the GUI version of PDF Toolkit.
"""

import sys
import os
import signal

# Add current directory to path to import gui modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
    from gui.main_window import MainWindow
except ImportError as e:
    print("❌ 錯誤：缺少必要的依賴")
    print(f"   {e}")
    print("\n請安裝 GUI 依賴：")
    print("   pip install -r requirements-gui.txt")
    sys.exit(1)


def main():
    """Launch the PDF Toolkit GUI application."""
    try:
        # Create and run the application
        app = MainWindow()

        def _handle_sigint(*_args):
            app.after(0, app.quit)

        signal.signal(signal.SIGINT, _handle_sigint)

        # Set application icon (if available)
        # try:
        #     app.iconbitmap("icon.ico")  # Windows
        # except:
        #     pass

        # Start the main loop
        app.mainloop()

    except KeyboardInterrupt:
        print("\n程式已終止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 啟動 GUI 時發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
