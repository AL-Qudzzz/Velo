import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from PIL import Image
import os
import threading
import time
from datetime import datetime
from pathlib import Path

# Set theme and color
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

from . import config

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("VeloBot - Modern WhatsApp Blaster")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Variables
        self.base_delay_var = tk.IntVar(value=config.BASE_DELAY)
        self.jitter_min_var = tk.IntVar(value=config.JITTER_MIN)
        self.jitter_max_var = tk.IntVar(value=config.JITTER_MAX)
        self.warmup_count_var = tk.IntVar(value=config.WARMUP_COUNT)
        self.warmup_delay_var = tk.IntVar(value=config.WARMUP_DELAY)
        self.use_fixed_delay_var = tk.BooleanVar(value=False)

        # Grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Setup sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VeloBot 🤖", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.sidebar_btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.sidebar_btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_btn_campaign = ctk.CTkButton(self.sidebar_frame, text="Campaign", command=self.show_campaign)
        self.sidebar_btn_campaign.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_btn_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings)
        self.sidebar_btn_settings.grid(row=3, column=0, padx=20, pady=10)

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # Main Content Area — grid so views can stack at the same cell
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Initialize Views (each must be placed at grid row=0,col=0)
        self._current_view = None
        self.create_dashboard_view()
        self.create_campaign_view()
        self.create_settings_view()

        # Show default view
        self.show_campaign()

    def create_dashboard_view(self):
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.dashboard_frame.grid_remove()  # Hidden by default
        
        # Status Cards
        status_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        status_container.pack(fill="x", pady=(0, 20))
        
        self.card_remaining = self.create_stat_card(status_container, "Remaining", "0", "blue")
        self.card_remaining.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.card_success = self.create_stat_card(status_container, "Success", "0", "green")
        self.card_success.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.card_failed = self.create_stat_card(status_container, "Failed", "0", "red")
        self.card_failed.pack(side="left", fill="x", expand=True)

        # Countdown & Info Area
        info_frame = ctk.CTkFrame(self.dashboard_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        self.countdown_label = ctk.CTkLabel(info_frame, text="--:--", font=ctk.CTkFont(size=40, weight="bold"), text_color="#FFA500")
        self.countdown_label.pack(pady=(20, 5))
        
        self.next_contact_label = ctk.CTkLabel(info_frame, text="Next: Waiting to start...", font=ctk.CTkFont(size=14))
        self.next_contact_label.pack(pady=(0, 20))

        # Log Console
        log_frame = ctk.CTkFrame(self.dashboard_frame)
        log_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(log_frame, text="Execution Log", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.log_console = ctk.CTkTextbox(log_frame, font=("Consolas", 12))
        self.log_console.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Control Buttons
        control_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        control_frame.pack(fill="x")
        
        self.btn_start = ctk.CTkButton(control_frame, text="▶ START CAMPAIGN", command=self.start_campaign, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="green")
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_pause = ctk.CTkButton(control_frame, text="⏸ PAUSE", command=self.pause_campaign, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="orange", state="disabled")
        self.btn_pause.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_stop = ctk.CTkButton(control_frame, text="⏹ STOP", command=self.stop_campaign, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="red", state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True)

    def create_stat_card(self, parent, title, value, color_theme):
        card = ctk.CTkFrame(parent)
        
        # Color accent stripe
        stripe = ctk.CTkFrame(card, height=3, fg_color=color_theme)
        stripe.pack(fill="x")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        value_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=color_theme)
        value_lbl.pack(pady=(0, 15))
        
        # Store reference to label for updates
        if title == "Remaining": self.lbl_remaining = value_lbl
        elif title == "Success": self.lbl_success = value_lbl
        elif title == "Failed": self.lbl_failed = value_lbl
            
        return card

    def start_campaign(self):
        if not hasattr(self, 'df') or self.df is None:
            messagebox.showerror("Error", "Please load a contact file in the Campaign tab first!")
            return
            
        # Get column mapping
        phone_col = self.phone_col_menu.get()
        if not phone_col or phone_col == "":
            messagebox.showerror("Error", "Please select a Phone Column in the Campaign tab!")
            return

        # Prepare contacts
        try:
            from . import data_processor
            mapping = {
                'phone': phone_col,
                'name': self.name_col_menu.get(),
                'message': self.message_col_menu.get()
            }
            default_msg = self.default_msg_box.get("1.0", "end").strip()
            
            self.contacts = data_processor.prepare_contacts(self.df, mapping, default_msg)
            
            if not self.contacts:
                messagebox.showerror("Error", "No valid contacts found!")
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare contacts: {str(e)}")
            return

        # Confirm start
        if not messagebox.askyesno("Confirm Start", f"Ready to send to {len(self.contacts)} contacts?\n\nBase Delay: {self.base_delay_var.get()}s"):
            return

        self.is_running = True
        self.is_paused = False
        self.current_index = 0
        self.failed_contacts = []
        self.driver = None

        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        
        # Switch to dashboard
        self.show_dashboard()
        
        # Start thread
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        try:
            from .whatsapp_bot import setup_driver, wait_for_whatsapp_load, send_message
            import time as time_module
            import random
            
            self.log("Initializing WebDriver...")
            self.driver = setup_driver()
            
            self.log("Waiting for WhatsApp Web login...")
            wait_for_whatsapp_load(self.driver)
            self.log("WhatsApp Web loaded!")
            
            success_count = 0
            failed_count = 0
            total = len(self.contacts)
            
            for i in range(self.current_index, total):
                if not self.is_running: break
                
                # Pause logic
                while self.is_paused and self.is_running:
                    time_module.sleep(1)
                    
                if not self.is_running: break
                
                contact = self.contacts[i]
                self.current_index = i
                
                # Update UI
                self.next_contact_label.configure(text=f"Sending to: {contact['name']} ({contact['phone']})")
                
                self.log(f"Sending to {contact['name']}...")
                
                # Send
                res = send_message(self.driver, contact['phone'], contact['message'], contact['name'])
                
                if res:
                    success_count += 1
                    self.lbl_success.configure(text=str(success_count))
                    self.log(f"✅ Sent to {contact['name']}")
                else:
                    failed_count += 1
                    self.lbl_failed.configure(text=str(failed_count))
                    self.log(f"❌ Failed to {contact['name']}")
                    self.failed_contacts.append(contact)

                self.lbl_remaining.configure(text=str(total - (i + 1)))

                # Delay logic (if not last)
                if i < total - 1:
                    delay = self.base_delay_var.get()
                    if not self.use_fixed_delay_var.get():
                         # Add jitter
                         jitter = random.uniform(self.jitter_min_var.get(), self.jitter_max_var.get())
                         delay += jitter
                         # Add warm-up
                         if i < self.warmup_count_var.get():
                             delay += self.warmup_delay_var.get()
                    
                    # Countdown
                    for t in range(int(delay), 0, -1):
                        if not self.is_running: break
                        while self.is_paused: time_module.sleep(1)
                        
                        self.countdown_label.configure(text=f"{t}s")
                        time_module.sleep(1)
                    
            self.log("Campaign Finished!")
            messagebox.showinfo("Done", f"Campaign finished.\nSuccess: {success_count}\nFailed: {failed_count}")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            if self.driver:
                self.driver.quit()
            self.is_running = False
            self.btn_start.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_stop.configure(state="disabled")

    def pause_campaign(self):
        if self.is_paused:
            self.is_paused = False
            self.btn_pause.configure(text="⏸ PAUSE", fg_color="orange")
            self.log("Resuming...")
        else:
            self.is_paused = True
            self.btn_pause.configure(text="▶ RESUME", fg_color="green")
            self.log("Paused.")
        
    def stop_campaign(self):
        if messagebox.askyesno("Stop", "Are you sure you want to stop?"):
            self.is_running = False
            self.log("Stopping...")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert("end", f"[{timestamp}] {message}\n")
        self.log_console.see("end")

    def create_campaign_view(self):
        self.campaign_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.campaign_frame.grid(row=0, column=0, sticky="nsew")
        self.campaign_frame.grid_remove()  # Hidden by default
        
        # File Selection Area
        file_frame = ctk.CTkFrame(self.campaign_frame)
        file_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(file_frame, text="1. Select Contact List (Excel/CSV)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        file_input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(file_input_frame, textvariable=self.file_path_var, placeholder_text="No file selected...", width=400)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(file_input_frame, text="Browse File", command=self.browse_file, width=100)
        self.browse_btn.pack(side="left", padx=(0, 10))
        
        self.load_btn = ctk.CTkButton(file_input_frame, text="Load Data", command=self.load_file, width=100, fg_color="green")
        self.load_btn.pack(side="left")

        # Data Preview Area
        preview_frame = ctk.CTkFrame(self.campaign_frame)
        preview_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(preview_frame, text="2. Data Preview (First 5 Rows)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.preview_table_frame = ctk.CTkScrollableFrame(preview_frame, height=150)
        self.preview_table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.preview_label = ctk.CTkLabel(self.preview_table_frame, text="No data loaded. Please browse and load a file.", text_color="gray")
        self.preview_label.pack(pady=20)

        # Column Mapping Area
        mapping_frame = ctk.CTkFrame(self.campaign_frame)
        mapping_frame.pack(fill="x")
        
        ctk.CTkLabel(mapping_frame, text="3. Map Columns", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        grid_frame = ctk.CTkFrame(mapping_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Phone
        ctk.CTkLabel(grid_frame, text="Phone Column *").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.phone_col_menu = ctk.CTkOptionMenu(grid_frame, values=["(Load File First)"])
        self.phone_col_menu.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Name
        ctk.CTkLabel(grid_frame, text="Name Column (Optional)").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.name_col_menu = ctk.CTkOptionMenu(grid_frame, values=["(Load File First)"])
        self.name_col_menu.grid(row=0, column=3, sticky="ew", padx=10, pady=5)
        
        # Message
        ctk.CTkLabel(grid_frame, text="Message Column (Optional)").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.message_col_menu = ctk.CTkOptionMenu(grid_frame, values=["(Load File First)"])
        self.message_col_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Default Message
        ctk.CTkLabel(grid_frame, text="Default Message").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
        self.default_msg_box = ctk.CTkTextbox(grid_frame, height=60)
        self.default_msg_box.grid(row=2, column=1, columnspan=3, sticky="ew", padx=10, pady=5)
        self.default_msg_box.insert("1.0", "Hello! This is a test message.")
        
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(3, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel or CSV file",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)

    def load_file(self):
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        
        try:
            # We need to import data_processor from src.
            # Ideally standard imports should be at top level, but for now we do this
            from . import data_processor
            
            self.df = data_processor.process_spreadsheet(filepath)
            self.setup_preview_table(self.df.head(5))
            self.update_column_mapping(self.df.columns.tolist())
            
            messagebox.showinfo("Success", f"Loaded {len(self.df)} rows successfully!")
            
        except ImportError:
            # If running as standalone script for testing without package context
             messagebox.showerror("Error", "Could not import data_processor. Make sure you run this from the project root.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def setup_preview_table(self, df_head):
        # Clear previous widgets
        for widget in self.preview_table_frame.winfo_children():
            widget.destroy()
            
        columns = df_head.columns.tolist()
        
        # Header
        for col_idx, col_name in enumerate(columns):
            lbl = ctk.CTkLabel(self.preview_table_frame, text=str(col_name), font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=5, pady=5, sticky="ew")
        
        # Rows
        for row_idx, row in df_head.iterrows():
            for col_idx, col_name in enumerate(columns):
                val = str(row[col_name])
                # Truncate long text
                if len(val) > 20: val = val[:17] + "..."
                
                lbl = ctk.CTkLabel(self.preview_table_frame, text=val)
                lbl.grid(row=row_idx+1, column=col_idx, padx=5, pady=2, sticky="ew")

    def update_column_mapping(self, columns):
        defaults = [""] + columns
        self.phone_col_menu.configure(values=defaults)
        self.name_col_menu.configure(values=defaults)
        self.message_col_menu.configure(values=defaults)
        
        # Auto-select if matches found (simple logic)
        for col in columns:
            lower = col.lower()
            if "phone" in lower or "nomor" in lower or "wa" in lower:
                self.phone_col_menu.set(col)
            elif "name" in lower or "nama" in lower:
                self.name_col_menu.set(col)
            elif "message" in lower or "pesan" in lower:
                self.message_col_menu.set(col)
    
        if self.phone_col_menu.get() == "(Load File First)":
             self.phone_col_menu.set("")
        if self.name_col_menu.get() == "(Load File First)":
             self.name_col_menu.set("")
        if self.message_col_menu.get() == "(Load File First)":
             self.message_col_menu.set("")

    def create_settings_view(self):
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
        self.settings_frame.grid_remove()  # Hidden by default

        # Delay Configuration
        delay_frame = ctk.CTkScrollableFrame(self.settings_frame)
        delay_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(delay_frame, text="Delay Configuration", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        # Base Delay
        self.create_slider(delay_frame, "Base Delay (seconds)", self.base_delay_var, 30, 300)
        
        # Jitter
        self.create_slider(delay_frame, "Jitter Min (seconds)", self.jitter_min_var, 0, 30)
        self.create_slider(delay_frame, "Jitter Max (seconds)", self.jitter_max_var, 0, 60)
        
        # Warm-up
        self.create_slider(delay_frame, "Warm-up Messages", self.warmup_count_var, 0, 20)
        self.create_slider(delay_frame, "Warm-up Extra Delay", self.warmup_delay_var, 0, 180)
        
        # Fixed Delay Mode
        self.fixed_delay_switch = ctk.CTkSwitch(delay_frame, text="Use Fixed Delay (No Randomization)", variable=self.use_fixed_delay_var, command=self.toggle_fixed_delay)
        self.fixed_delay_switch.pack(anchor="w", padx=20, pady=10)

        # Presets
        preset_frame = ctk.CTkFrame(self.settings_frame)
        preset_frame.pack(fill="x")
        
        ctk.CTkLabel(preset_frame, text="Quick Presets", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        btn_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="Safe (Recommended)", fg_color="green", command=lambda: self.apply_preset("safe")).pack(side="left", padx=(0, 10), expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Moderate", fg_color="orange", command=lambda: self.apply_preset("moderate")).pack(side="left", padx=(0, 10), expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Fast (Risky)", fg_color="red", command=lambda: self.apply_preset("fast")).pack(side="left", padx=(0, 10), expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Fixed 3min", fg_color="purple", command=lambda: self.apply_preset("fixed3")).pack(side="left", expand=True, fill="x")

    def create_slider(self, parent, label_text, variable, min_val, max_val):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
        label.pack(side="left")
        
        value_label = ctk.CTkLabel(frame, text=str(int(variable.get())), width=30)
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=variable, 
                               command=lambda v, l=value_label: l.configure(text=str(int(v))))
        slider.pack(side="left", fill="x", expand=True, padx=10)

    def toggle_fixed_delay(self):
        # Logic to disable sliders could go here, for now just visual toggle
        pass
        
    def apply_preset(self, preset_name):
        presets = {
            "safe": {"base": 60, "j_min": 10, "j_max": 20, "w_count": 5, "w_delay": 90, "fixed": False},
            "moderate": {"base": 45, "j_min": 5, "j_max": 15, "w_count": 3, "w_delay": 60, "fixed": False},
            "fast": {"base": 30, "j_min": 3, "j_max": 10, "w_count": 2, "w_delay": 30, "fixed": False},
            "fixed3": {"base": 180, "j_min": 0, "j_max": 0, "w_count": 0, "w_delay": 0, "fixed": True}
        }
        
        if preset_name in presets:
            p = presets[preset_name]
            self.base_delay_var.set(p["base"])
            self.jitter_min_var.set(p["j_min"])
            self.jitter_max_var.set(p["j_max"])
            self.warmup_count_var.set(p["w_count"])
            self.warmup_delay_var.set(p["w_delay"])
            self.use_fixed_delay_var.set(p["fixed"])
            # sliders update automatically via IntVar/BooleanVar binding
            messagebox.showinfo("Preset Applied", f"Applied '{preset_name}' preset successfully!")

    # -------------------------------------------------------------------------
    # View navigation
    # -------------------------------------------------------------------------
    def show_view(self, view_frame):
        """Hide all views, then reveal the requested one using grid."""
        all_views = [
            self.dashboard_frame,
            self.campaign_frame,
            self.settings_frame,
        ]
        for frame in all_views:
            frame.grid_remove()
        view_frame.grid()  # Makes it visible at its pre-configured grid position
        self._current_view = view_frame

        # Update sidebar button highlights
        btn_map = {
            self.dashboard_frame: self.sidebar_btn_dashboard,
            self.campaign_frame:  self.sidebar_btn_campaign,
            self.settings_frame:  self.sidebar_btn_settings,
        }
        for frm, btn in btn_map.items():
            if frm is view_frame:
                btn.configure(fg_color=("#3B82F6", "#1D4ED8"))
            else:
                btn.configure(fg_color=("gray75", "gray25"))

    def show_dashboard(self):
        self.show_view(self.dashboard_frame)

    def show_campaign(self):
        self.show_view(self.campaign_frame)

    def show_settings(self):
        self.show_view(self.settings_frame)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
