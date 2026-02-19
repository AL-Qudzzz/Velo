"""
AutoBlast WhatsApp Bot - Main Entry Point
GUI Application launcher for Windows executable build
"""

import sys
import tkinter as tk
from tkinter import messagebox

def main():
    """Main entry point for the application"""
    try:
        # Import the GUI application
        from src.whatsapp_bot_gui import WhatsAppBotGUI
        
        # Create root window
        root = tk.Tk()
        
        # Create application instance
        app = WhatsAppBotGUI(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Failed to import required modules:\n{str(e)}\n\nPlease ensure all dependencies are installed."
        if 'tk' in sys.modules:
            messagebox.showerror("Import Error", error_msg)
        else:
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
