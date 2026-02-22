"""
AutoBlast — Main Entry Point
Run with:  python main.py   (or double-click AutoBlast.bat)
"""
import sys
import os

def main():
    # Add project root so 'src' package is importable
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    try:
        from src.utils import check_chrome_installed
        if not check_chrome_installed():
            import tkinter as tk
            from tkinter import messagebox
            root_win = tk.Tk(); root_win.withdraw()
            messagebox.showerror(
                "Chrome Not Found",
                "Google Chrome is required but was not detected.\n"
                "Please install Chrome and try again.")
            sys.exit(1)
    except Exception:
        pass  # Skip chrome check if utils fails to import

    try:
        from src.modern_gui import AutoBlastApp
        app = AutoBlastApp()
        app.mainloop()
    except ImportError as e:
        _fatal(f"Failed to import required modules:\n{e}\n\n"
               "Please run:  scripts\\setup_venv.bat\nto install dependencies.")
    except Exception as e:
        _fatal(f"Unexpected error:\n{e}")


def _fatal(msg: str):
    """Show error in a messagebox if possible, otherwise print."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw()
        messagebox.showerror("AutoBlast — Error", msg)
    except Exception:
        print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
