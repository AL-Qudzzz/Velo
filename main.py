"""
AutoBlast WhatsApp Bot - Main Entry Point
GUI Application launcher for Windows executable build
"""

import sys
import tkinter as tk
from tkinter import messagebox
import os

def main():
    """Main entry point for the application"""
    # Create src directory if not exists
    if not os.path.exists("src"):
        os.makedirs("src")

    try:
        # Check for Chrome
        from src.utils import check_chrome_installed
        if not check_chrome_installed():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", "Google Chrome not found! Please install Chrome to use this bot.")
            sys.exit(1)

        # Run Modern GUI
        from src.modern_gui import ModernApp
        app = ModernApp()
        app.mainloop()

    except ImportError as e:
        error_msg = f"Failed to import required modules:\n{str(e)}\n\nPlease ensure all dependencies are installed."
        # Attempt to use tkinter messagebox if possible, otherwise print to stderr
        try:
            root = tk.Tk()
            root.withdraw() # Hide the main window
            messagebox.showerror("Import Error", error_msg)
        except tk.TclError: # Catch error if Tkinter is not available/initialized
            print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"An unexpected error occurred:\n{str(e)}"
        if 'tk' in sys.modules:
            try:
                messagebox.showerror("Application Error", error_msg)
            except:
                print(f"ERROR: {error_msg}", file=sys.stderr)
        else:
            print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
