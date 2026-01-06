"""
WhatsApp Bot GUI Application
Tkinter-based graphical user interface for easy bot configuration and execution
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

import config
import utils
import data_processor
from whatsapp_bot import setup_driver, wait_for_whatsapp_load, send_message, detect_invalid_number

class WhatsAppBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bot Blasting System")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.file_path = tk.StringVar()
        self.df = None
        self.column_mapping = {}
        self.contacts = []
        self.is_running = False
        self.driver = None
        
        # Delay settings variables
        self.base_delay = tk.IntVar(value=config.BASE_DELAY)
        self.jitter_min = tk.IntVar(value=config.JITTER_MIN)
        self.jitter_max = tk.IntVar(value=config.JITTER_MAX)
        self.warmup_count = tk.IntVar(value=config.WARMUP_COUNT)
        self.warmup_delay = tk.IntVar(value=config.WARMUP_DELAY)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title
        title_frame = tk.Frame(self.root, bg="#25D366", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 WhatsApp Bot Blasting System",
            font=("Arial", 18, "bold"),
            bg="#25D366",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main container with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: File & Columns
        tab1 = tk.Frame(notebook)
        notebook.add(tab1, text="📁 File & Columns")
        self.setup_file_tab(tab1)
        
        # Tab 2: Delay Settings
        tab2 = tk.Frame(notebook)
        notebook.add(tab2, text="⏱️ Delay Settings")
        self.setup_delay_tab(tab2)
        
        # Tab 3: Execution
        tab3 = tk.Frame(notebook)
        notebook.add(tab3, text="▶️ Execution")
        self.setup_execution_tab(tab3)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#f0f0f0"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_file_tab(self, parent):
        """Setup file selection and column mapping tab"""
        
        # File selection frame
        file_frame = tk.LabelFrame(parent, text="Excel/CSV File", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Load File", command=self.load_file, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Preview frame
        preview_frame = tk.LabelFrame(parent, text="Data Preview", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, width=80, font=("Courier", 9))
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Column mapping frame
        mapping_frame = tk.LabelFrame(parent, text="Column Mapping", padx=10, pady=10)
        mapping_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Phone column
        tk.Label(mapping_frame, text="Phone Column:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_combo = ttk.Combobox(mapping_frame, width=30, state="readonly")
        self.phone_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Name column
        tk.Label(mapping_frame, text="Name Column (optional):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_combo = ttk.Combobox(mapping_frame, width=30, state="readonly")
        self.name_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Message column
        tk.Label(mapping_frame, text="Message Column (optional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.message_combo = ttk.Combobox(mapping_frame, width=30, state="readonly")
        self.message_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Default message
        tk.Label(mapping_frame, text="Default Message:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.default_message = tk.Text(mapping_frame, height=3, width=40)
        self.default_message.grid(row=3, column=1, padx=5, pady=5)
        self.default_message.insert("1.0", "Hello! This is a test message.")
        
        tk.Button(mapping_frame, text="Auto-Detect Columns", command=self.auto_detect_columns, bg="#FF9800", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
    
    def setup_delay_tab(self, parent):
        """Setup delay configuration tab"""
        
        info_frame = tk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = """⚠️ IMPORTANT: Delay settings are critical for avoiding WhatsApp bans.
Lower delays = higher risk of account suspension. Use with caution!"""
        
        info_label = tk.Label(info_frame, text=info_text, bg="#FFF3CD", fg="#856404", 
                             justify=tk.LEFT, padx=10, pady=10, wraplength=800)
        info_label.pack(fill=tk.X)
        
        # Settings frame
        settings_frame = tk.LabelFrame(parent, text="Delay Configuration", padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Base delay
        row = 0
        tk.Label(settings_frame, text="Base Delay (seconds):", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Scale(settings_frame, from_=30, to=180, orient=tk.HORIZONTAL, variable=self.base_delay, 
                length=300, command=self.update_estimate).grid(row=row, column=1, padx=10)
        self.base_delay_label = tk.Label(settings_frame, text=f"{self.base_delay.get()}s")
        self.base_delay_label.grid(row=row, column=2)
        
        # Jitter min
        row += 1
        tk.Label(settings_frame, text="Jitter Min (seconds):", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Scale(settings_frame, from_=0, to=30, orient=tk.HORIZONTAL, variable=self.jitter_min, 
                length=300, command=self.update_estimate).grid(row=row, column=1, padx=10)
        self.jitter_min_label = tk.Label(settings_frame, text=f"{self.jitter_min.get()}s")
        self.jitter_min_label.grid(row=row, column=2)
        
        # Jitter max
        row += 1
        tk.Label(settings_frame, text="Jitter Max (seconds):", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Scale(settings_frame, from_=0, to=60, orient=tk.HORIZONTAL, variable=self.jitter_max, 
                length=300, command=self.update_estimate).grid(row=row, column=1, padx=10)
        self.jitter_max_label = tk.Label(settings_frame, text=f"{self.jitter_max.get()}s")
        self.jitter_max_label.grid(row=row, column=2)
        
        # Warmup count
        row += 1
        tk.Label(settings_frame, text="Warm-up Messages:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Scale(settings_frame, from_=0, to=20, orient=tk.HORIZONTAL, variable=self.warmup_count, 
                length=300, command=self.update_estimate).grid(row=row, column=1, padx=10)
        self.warmup_count_label = tk.Label(settings_frame, text=f"{self.warmup_count.get()} messages")
        self.warmup_count_label.grid(row=row, column=2)
        
        # Warmup delay
        row += 1
        tk.Label(settings_frame, text="Warm-up Extra Delay (seconds):", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Scale(settings_frame, from_=0, to=180, orient=tk.HORIZONTAL, variable=self.warmup_delay, 
                length=300, command=self.update_estimate).grid(row=row, column=1, padx=10)
        self.warmup_delay_label = tk.Label(settings_frame, text=f"{self.warmup_delay.get()}s")
        self.warmup_delay_label.grid(row=row, column=2)
        
        # Estimate
        row += 1
        estimate_frame = tk.Frame(settings_frame, bg="#E3F2FD", padx=10, pady=10)
        estimate_frame.grid(row=row, column=0, columnspan=3, pady=20, sticky=tk.EW)
        
        tk.Label(estimate_frame, text="📊 Estimated Time:", font=("Arial", 11, "bold"), bg="#E3F2FD").pack()
        self.estimate_label = tk.Label(estimate_frame, text="Load file to see estimate", 
                                       font=("Arial", 10), bg="#E3F2FD", fg="#1976D2")
        self.estimate_label.pack()
        
        # Preset buttons
        row += 1
        preset_frame = tk.Frame(settings_frame)
        preset_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        tk.Label(preset_frame, text="Quick Presets:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(preset_frame, text="🐢 Safe (Recommended)", command=lambda: self.apply_preset("safe"), 
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(preset_frame, text="⚡ Moderate", command=lambda: self.apply_preset("moderate"), 
                 bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(preset_frame, text="🚀 Fast (Risky)", command=lambda: self.apply_preset("fast"), 
                 bg="#F44336", fg="white").pack(side=tk.LEFT, padx=5)
    
    def setup_execution_tab(self, parent):
        """Setup execution and monitoring tab"""
        
        # Control buttons
        control_frame = tk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(control_frame, text="▶️ Start Sending", command=self.start_bot, 
                                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_button = tk.Button(control_frame, text="⏹️ Stop", command=self.stop_bot, 
                                     bg="#F44336", fg="white", font=("Arial", 12, "bold"), height=2, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Progress frame
        progress_frame = tk.LabelFrame(parent, text="Progress", padx=10, pady=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="0 / 0 messages sent", font=("Arial", 10))
        self.progress_label.pack()
        
        # Log frame
        log_frame = tk.LabelFrame(parent, text="Execution Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(parent, text="Statistics", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack()
        
        tk.Label(stats_grid, text="Success:", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10)
        self.success_label = tk.Label(stats_grid, text="0", font=("Arial", 9), fg="green")
        self.success_label.grid(row=0, column=1, padx=10)
        
        tk.Label(stats_grid, text="Failed:", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=10)
        self.failed_label = tk.Label(stats_grid, text="0", font=("Arial", 9), fg="red")
        self.failed_label.grid(row=0, column=3, padx=10)
        
        tk.Label(stats_grid, text="Remaining:", font=("Arial", 9, "bold")).grid(row=0, column=4, padx=10)
        self.remaining_label = tk.Label(stats_grid, text="0", font=("Arial", 9), fg="blue")
        self.remaining_label.grid(row=0, column=5, padx=10)
    
    def browse_file(self):
        """Browse for Excel/CSV file"""
        filename = filedialog.askopenfilename(
            title="Select Excel or CSV file",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
    
    def load_file(self):
        """Load and preview the selected file"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        try:
            self.df = data_processor.process_spreadsheet(self.file_path.get())
            
            # Update preview
            preview = f"File: {Path(self.file_path.get()).name}\n"
            preview += f"Rows: {len(self.df)}, Columns: {len(self.df.columns)}\n\n"
            preview += self.df.head(5).to_string(index=False)
            
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", preview)
            
            # Update column dropdowns
            columns = [""] + list(self.df.columns)
            self.phone_combo['values'] = columns
            self.name_combo['values'] = columns
            self.message_combo['values'] = columns
            
            self.log("File loaded successfully!")
            self.update_status(f"Loaded: {len(self.df)} rows")
            self.update_estimate()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")
    
    def auto_detect_columns(self):
        """Auto-detect columns"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a file first!")
            return
        
        detected = data_processor.detect_columns(self.df)
        
        if detected['phone']:
            self.phone_combo.set(detected['phone'])
        if detected['name']:
            self.name_combo.set(detected['name'])
        if detected['message']:
            self.message_combo.set(detected['message'])
        
        self.log("Auto-detection completed!")
        messagebox.showinfo("Auto-Detection", 
                           f"Detected:\nPhone: {detected['phone'] or 'Not found'}\n"
                           f"Name: {detected['name'] or 'Not found'}\n"
                           f"Message: {detected['message'] or 'Not found'}")
    
    def apply_preset(self, preset_name):
        """Apply delay preset"""
        presets = {
            "safe": {
                "base_delay": 60,
                "jitter_min": 10,
                "jitter_max": 20,
                "warmup_count": 5,
                "warmup_delay": 90
            },
            "moderate": {
                "base_delay": 45,
                "jitter_min": 5,
                "jitter_max": 15,
                "warmup_count": 3,
                "warmup_delay": 60
            },
            "fast": {
                "base_delay": 30,
                "jitter_min": 3,
                "jitter_max": 10,
                "warmup_count": 2,
                "warmup_delay": 30
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.base_delay.set(preset["base_delay"])
            self.jitter_min.set(preset["jitter_min"])
            self.jitter_max.set(preset["jitter_max"])
            self.warmup_count.set(preset["warmup_count"])
            self.warmup_delay.set(preset["warmup_delay"])
            self.update_estimate()
            self.log(f"Applied preset: {preset_name.upper()}")
    
    def update_estimate(self, *args):
        """Update time estimate"""
        self.base_delay_label.config(text=f"{self.base_delay.get()}s")
        self.jitter_min_label.config(text=f"{self.jitter_min.get()}s")
        self.jitter_max_label.config(text=f"{self.jitter_max.get()}s")
        self.warmup_count_label.config(text=f"{self.warmup_count.get()} messages")
        self.warmup_delay_label.config(text=f"{self.warmup_delay.get()}s")
        
        if self.df is not None:
            total = len(self.df)
            avg_delay = self.base_delay.get() + (self.jitter_min.get() + self.jitter_max.get()) / 2
            warmup_extra = self.warmup_delay.get() * min(total, self.warmup_count.get())
            estimated_seconds = (avg_delay * total) + warmup_extra
            
            hours = int(estimated_seconds // 3600)
            minutes = int((estimated_seconds % 3600) // 60)
            
            estimate_text = f"For {total} messages: ~{hours}h {minutes}m"
            self.estimate_label.config(text=estimate_text)
    
    def start_bot(self):
        """Start the bot in a separate thread"""
        if self.df is None:
            messagebox.showerror("Error", "Please load a file first!")
            return
        
        if not self.phone_combo.get():
            messagebox.showerror("Error", "Please select the phone column!")
            return
        
        # Prepare column mapping
        self.column_mapping = {
            'phone': self.phone_combo.get(),
            'name': self.name_combo.get() if self.name_combo.get() else None,
            'message': self.message_combo.get() if self.message_combo.get() else None
        }
        
        # Get default message
        default_msg = self.default_message.get("1.0", tk.END).strip()
        
        # Prepare contacts
        self.contacts = data_processor.prepare_contacts(self.df, self.column_mapping, default_msg)
        
        if not self.contacts:
            messagebox.showerror("Error", "No valid contacts found!")
            return
        
        # Confirm
        if not messagebox.askyesno("Confirm", 
                                   f"Ready to send {len(self.contacts)} messages?\n\n"
                                   f"Base delay: {self.base_delay.get()}s\n"
                                   f"Jitter: {self.jitter_min.get()}-{self.jitter_max.get()}s\n\n"
                                   "Continue?"):
            return
        
        # Update UI
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar['maximum'] = len(self.contacts)
        self.progress_bar['value'] = 0
        
        # Start in thread
        thread = threading.Thread(target=self.run_bot, daemon=True)
        thread.start()
    
    def run_bot(self):
        """Run the bot (in separate thread)"""
        try:
            self.log("="*60)
            self.log("Starting WhatsApp Bot...")
            self.log("="*60)
            
            # Setup driver
            self.log("Initializing Chrome WebDriver...")
            self.driver = setup_driver()
            
            # Load WhatsApp
            self.log("Loading WhatsApp Web...")
            wait_for_whatsapp_load(self.driver)
            self.log("WhatsApp Web loaded successfully!")
            
            # Send messages
            success_count = 0
            failed_count = 0
            
            for idx, contact in enumerate(self.contacts):
                if not self.is_running:
                    self.log("Stopped by user")
                    break
                
                message_num = idx + 1
                self.log(f"\n[{message_num}/{len(self.contacts)}] Processing {contact['name']}...")
                
                # Send message
                success = send_message(
                    self.driver,
                    contact['phone'],
                    contact['message'],
                    contact['name']
                )
                
                if success:
                    success_count += 1
                    self.log(f"✓ Message sent to {contact['name']} ({contact['phone']})")
                else:
                    failed_count += 1
                    self.log(f"✗ Failed to send to {contact['name']} ({contact['phone']})")
                
                # Update UI
                self.root.after(0, self.update_progress, message_num, success_count, failed_count)
                
                # Delay
                if message_num < len(self.contacts):
                    delay = self.calculate_custom_delay(message_num)
                    self.log(f"Waiting {delay:.1f}s before next message...")
                    
                    # Wait with ability to stop
                    for _ in range(int(delay)):
                        if not self.is_running:
                            break
                        import time
                        time.sleep(1)
            
            self.log("\n" + "="*60)
            self.log("COMPLETED!")
            self.log(f"Success: {success_count}, Failed: {failed_count}")
            self.log("="*60)
            
            messagebox.showinfo("Complete", 
                              f"Finished sending messages!\n\n"
                              f"Success: {success_count}\n"
                              f"Failed: {failed_count}")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
            self.is_running = False
            self.root.after(0, self.reset_ui)
    
    def calculate_custom_delay(self, message_count):
        """Calculate delay with custom settings"""
        import random
        
        delay = self.base_delay.get()
        
        if message_count < self.warmup_count.get():
            delay += self.warmup_delay.get()
        
        jitter = random.uniform(self.jitter_min.get(), self.jitter_max.get())
        delay += jitter
        
        return delay
    
    def stop_bot(self):
        """Stop the bot"""
        if messagebox.askyesno("Confirm", "Are you sure you want to stop?"):
            self.is_running = False
            self.log("Stopping...")
    
    def update_progress(self, current, success, failed):
        """Update progress UI"""
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"{current} / {len(self.contacts)} messages sent")
        self.success_label.config(text=str(success))
        self.failed_label.config(text=str(failed))
        self.remaining_label.config(text=str(len(self.contacts) - current))
    
    def reset_ui(self):
        """Reset UI after completion"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Ready")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.root.after(0, self._append_log, log_entry)
    
    def _append_log(self, text):
        """Append to log (thread-safe)"""
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)

def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = WhatsAppBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
