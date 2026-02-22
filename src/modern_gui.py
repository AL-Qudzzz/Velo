"""
AutoBlast — Modern GUI (Unified)
Single entry-point application using CustomTkinter (dark mode).
Features: Campaign setup, Delay settings, Anti-Ban auto-pause, Live dashboard,
          Progress save/resume, Failed contacts export.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import json
import random
import time as time_module
from datetime import datetime
from pathlib import Path

from . import config
from . import data_processor
from .whatsapp_bot import setup_driver, wait_for_whatsapp_load, send_message

# ─── Theme ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AutoBlastApp(ctk.CTk):
    """Main application window — all views in one class."""

    # ─────────────────────────────────────────────────────────────────────────
    # INIT
    # ─────────────────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()

        self.title("AutoBlast 🤖 — WhatsApp Blaster")
        self.geometry("1150x720")
        self.minsize(950, 600)

        # ── Bot State ────────────────────────────────────────────────────────
        self.df = None
        self.contacts: list = []
        self.failed_contacts: list = []
        self.driver = None
        self.is_running = False
        self.is_paused = False
        self.current_index = 0
        self._session_success = 0       # per-run success counter for auto-pause

        # ── Auto-resume ──────────────────────────────────────────────────────
        self._auto_resume_cancel = threading.Event()
        self._auto_resume_thread = None

        # ── Progress file ────────────────────────────────────────────────────
        self.progress_file = Path(__file__).parent / "progress_gui.json"

        # ── Delay vars (tk) ──────────────────────────────────────────────────
        self.v_base_delay    = tk.IntVar(value=config.BASE_DELAY)
        self.v_jitter_min    = tk.IntVar(value=config.JITTER_MIN)
        self.v_jitter_max    = tk.IntVar(value=config.JITTER_MAX)
        self.v_warmup_count  = tk.IntVar(value=config.WARMUP_COUNT)
        self.v_warmup_delay  = tk.IntVar(value=config.WARMUP_DELAY)
        self.v_fixed_delay   = tk.BooleanVar(value=False)

        # ── Anti-Ban vars ────────────────────────────────────────────────────
        self.v_pause_limit   = tk.IntVar(value=config.PAUSE_LIMIT)
        self.v_auto_resume   = tk.BooleanVar(value=config.AUTO_RESUME_ENABLED)
        self.v_resume_hours  = tk.DoubleVar(value=config.AUTO_RESUME_HOURS)

        # ── UI ───────────────────────────────────────────────────────────────
        self._build_layout()
        self._check_resume_on_startup()

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT BUILDER
    # ─────────────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=190, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(sidebar, text="AutoBlast 🤖",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(24, 16))

        nav_items = [
            ("📊 Dashboard",  self._show_dashboard),
            ("📁 Campaign",   self._show_campaign),
            ("⏱️ Delay",      self._show_delay),
            ("🛡️ Anti-Ban",   self._show_antiban),
            ("⚙️ Settings",   self._show_settings),
        ]
        self._nav_buttons = {}
        for idx, (label, cmd) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(sidebar, text=label, command=cmd,
                                anchor="w", width=150)
            btn.grid(row=idx, column=0, padx=20, pady=6)
            self._nav_buttons[label] = btn

        # Appearance at bottom
        ctk.CTkLabel(sidebar, text="Theme:", anchor="w").grid(
            row=7, column=0, padx=20, pady=(10, 0))
        om = ctk.CTkOptionMenu(sidebar, values=["Dark", "Light", "System"],
                               command=lambda m: ctk.set_appearance_mode(m))
        om.grid(row=8, column=0, padx=20, pady=(4, 20))
        om.set("Dark")

        # ── Content area ─────────────────────────────────────────────────────
        self._content = ctk.CTkFrame(self, corner_radius=0,
                                     fg_color="transparent")
        self._content.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # Build all views
        self._views = {}
        self._build_dashboard()
        self._build_campaign()
        self._build_delay()
        self._build_antiban()
        self._build_settings()

        # Default view
        self._show_campaign()

    # ═════════════════════════════════════════════════════════════════════════
    # VIEW: DASHBOARD
    # ═════════════════════════════════════════════════════════════════════════
    def _build_dashboard(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._views["dash"] = f

        f.grid_rowconfigure(2, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # ── Stat cards ───────────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(f, fg_color="transparent")
        cards_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for col in range(3): cards_row.grid_columnconfigure(col, weight=1)

        def _card(parent, col, title, color):
            card = ctk.CTkFrame(parent)
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 8, 0))
            ctk.CTkFrame(card, height=3, fg_color=color).pack(fill="x")
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=12)).pack(pady=(8, 2))
            lbl = ctk.CTkLabel(card, text="0",
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color=color)
            lbl.pack(pady=(0, 12))
            return lbl

        self._lbl_remaining = _card(cards_row, 0, "Remaining", "#3B82F6")
        self._lbl_success   = _card(cards_row, 1, "Success",   "#22C55E")
        self._lbl_failed    = _card(cards_row, 2, "Failed",    "#EF4444")

        # ── Countdown / next contact ─────────────────────────────────────────
        info = ctk.CTkFrame(f)
        info.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._lbl_countdown = ctk.CTkLabel(
            info, text="--:--",
            font=ctk.CTkFont(size=40, weight="bold"), text_color="#FFA500")
        self._lbl_countdown.pack(pady=(16, 4))
        self._lbl_next = ctk.CTkLabel(
            info, text="Next: Waiting to start...",
            font=ctk.CTkFont(size=13))
        self._lbl_next.pack(pady=(0, 16))

        # ── Log console ──────────────────────────────────────────────────────
        log_f = ctk.CTkFrame(f)
        log_f.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        log_f.grid_rowconfigure(1, weight=1)
        log_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_f, text="Execution Log",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(8, 0))
        self._log_box = ctk.CTkTextbox(
            log_f, font=("Consolas", 11), state="disabled")
        self._log_box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 12))

        # ── Control buttons ──────────────────────────────────────────────────
        ctrl = ctk.CTkFrame(f, fg_color="transparent")
        ctrl.grid(row=3, column=0, sticky="ew")
        ctrl.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._btn_start = ctk.CTkButton(
            ctrl, text="▶  START", height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#16A34A", hover_color="#15803D",
            command=self._start_campaign)
        self._btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self._btn_pause = ctk.CTkButton(
            ctrl, text="⏸  PAUSE", height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#D97706", hover_color="#B45309",
            command=self._toggle_pause, state="disabled")
        self._btn_pause.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self._btn_stop = ctk.CTkButton(
            ctrl, text="⏹  STOP", height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self._stop_campaign, state="disabled")
        self._btn_stop.grid(row=0, column=2, sticky="ew", padx=(0, 6))

        self._btn_export = ctk.CTkButton(
            ctrl, text="📄 Export Failed", height=46,
            font=ctk.CTkFont(size=13),
            fg_color="#475569", hover_color="#334155",
            command=self._export_failed)
        self._btn_export.grid(row=0, column=3, sticky="ew")

    # ═════════════════════════════════════════════════════════════════════════
    # VIEW: CAMPAIGN
    # ═════════════════════════════════════════════════════════════════════════
    def _build_campaign(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._views["campaign"] = f
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # ── File / URL Selection ──────────────────────────────────────────────
        file_f = ctk.CTkFrame(f)
        file_f.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(file_f, text="1. Load Contact List",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4))

        # Mode toggle (File vs URL)
        mode_row = ctk.CTkFrame(file_f, fg_color="transparent")
        mode_row.pack(fill="x", padx=16, pady=(0, 8))
        self._v_input_mode = tk.StringVar(value="file")
        ctk.CTkRadioButton(mode_row, text="📁 File (Excel / CSV)",
                           variable=self._v_input_mode, value="file",
                           command=self._toggle_input_mode).pack(
            side="left", padx=(0, 20))
        ctk.CTkRadioButton(mode_row, text="🔗 Google Sheets Link",
                           variable=self._v_input_mode, value="url",
                           command=self._toggle_input_mode).pack(side="left")

        # File input row
        self._file_input_row = ctk.CTkFrame(file_f, fg_color="transparent")
        self._file_input_row.pack(fill="x", padx=16, pady=(0, 4))
        self._v_filepath = tk.StringVar()
        ctk.CTkEntry(self._file_input_row, textvariable=self._v_filepath,
                     placeholder_text="No file selected…").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(self._file_input_row, text="Browse", width=90,
                      command=self._browse_file).pack(side="left", padx=(0, 8))
        ctk.CTkButton(self._file_input_row, text="Load Data", width=100,
                      fg_color="#16A34A", hover_color="#15803D",
                      command=self._load_file).pack(side="left")

        # URL input row (hidden by default)
        self._url_input_row = ctk.CTkFrame(file_f, fg_color="transparent")
        self._v_sheets_url = tk.StringVar()
        ctk.CTkEntry(self._url_input_row, textvariable=self._v_sheets_url,
                     placeholder_text="https://docs.google.com/spreadsheets/d/…",
                     width=500).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(self._url_input_row, text="Load from URL", width=130,
                      fg_color="#16A34A", hover_color="#15803D",
                      command=self._load_file).pack(side="left")

        # Help text for URL mode
        self._lbl_url_help = ctk.CTkLabel(
            file_f,
            text="ℹ️  Spreadsheet harus di-share ke 'Anyone with the link can view' (publik)",
            text_color="#6B7280", font=ctk.CTkFont(size=11))

        # Spacer below input
        ctk.CTkFrame(file_f, fg_color="transparent", height=8).pack()

        # ── Preview table ─────────────────────────────────────────────────────
        prev_f = ctk.CTkFrame(f)
        prev_f.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        prev_f.grid_rowconfigure(1, weight=1)
        prev_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(prev_f, text="2. Data Preview (first 5 rows)",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 0))
        self._preview_scroll = ctk.CTkScrollableFrame(prev_f, height=160)
        self._preview_scroll.grid(row=1, column=0, sticky="nsew",
                                   padx=16, pady=(6, 16))
        self._lbl_preview_placeholder = ctk.CTkLabel(
            self._preview_scroll,
            text="No data loaded. Browse and load a file.",
            text_color="gray")
        self._lbl_preview_placeholder.pack(pady=20)

        # ── Column mapping ────────────────────────────────────────────────────
        map_f = ctk.CTkFrame(f)
        map_f.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(map_f, text="3. Map Columns",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 6))

        grid_f = ctk.CTkFrame(map_f, fg_color="transparent")
        grid_f.pack(fill="x", padx=16, pady=(0, 12))
        grid_f.columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(grid_f, text="Phone Column *").grid(
            row=0, column=0, sticky="w", padx=8, pady=5)
        self._om_phone = ctk.CTkOptionMenu(grid_f, values=["(Load File First)"])
        self._om_phone.grid(row=0, column=1, sticky="ew", padx=8, pady=5)

        ctk.CTkLabel(grid_f, text="Name Column").grid(
            row=0, column=2, sticky="w", padx=8, pady=5)
        self._om_name = ctk.CTkOptionMenu(grid_f, values=["(Load File First)"])
        self._om_name.grid(row=0, column=3, sticky="ew", padx=8, pady=5)

        ctk.CTkLabel(grid_f, text="Message Column").grid(
            row=1, column=0, sticky="w", padx=8, pady=5)
        self._om_message = ctk.CTkOptionMenu(
            grid_f, values=["(Load File First)"])
        self._om_message.grid(row=1, column=1, sticky="ew", padx=8, pady=5)

        ctk.CTkLabel(grid_f, text="Default Message").grid(
            row=2, column=0, sticky="nw", padx=8, pady=5)
        self._txt_default_msg = ctk.CTkTextbox(grid_f, height=70)
        self._txt_default_msg.grid(row=2, column=1, columnspan=3,
                                    sticky="ew", padx=8, pady=5)
        self._txt_default_msg.insert("1.0", "Hello {Name}! This is a message from us.")

        # ── Start button shortcut ─────────────────────────────────────────────
        ctk.CTkButton(
            f, text="▶  Start Campaign →", height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#16A34A", hover_color="#15803D",
            command=self._start_campaign
        ).grid(row=3, column=0, sticky="ew", pady=(8, 0))

    # ═════════════════════════════════════════════════════════════════════════
    # VIEW: DELAY
    # ═════════════════════════════════════════════════════════════════════════
    def _build_delay(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._views["delay"] = f
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(f)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="⏱️  Delay Configuration",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(16, 4))

        warn = ctk.CTkFrame(scroll, fg_color="#78350F")
        warn.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkLabel(
            warn,
            text="⚠️  Lower delays = higher risk of WhatsApp account ban. Use with caution!",
            text_color="#FDE68A", wraplength=700
        ).pack(padx=12, pady=8)

        self._slider_widgets = {}

        def _make_slider(parent, label, var, lo, hi):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row, text=label, width=200,
                         anchor="w").grid(row=0, column=0)
            val_lbl = ctk.CTkLabel(row, text=str(var.get()), width=50)
            val_lbl.grid(row=0, column=2)
            sl = ctk.CTkSlider(
                row, from_=lo, to=hi, variable=var,
                command=lambda v, l=val_lbl: l.configure(text=str(int(v))))
            sl.grid(row=0, column=1, sticky="ew", padx=10)
            self._slider_widgets[label] = sl

        _make_slider(scroll, "Base Delay (seconds)",
                     self.v_base_delay, 10, 300)
        _make_slider(scroll, "Jitter Min (seconds)",
                     self.v_jitter_min, 0, 30)
        _make_slider(scroll, "Jitter Max (seconds)",
                     self.v_jitter_max, 0, 60)
        _make_slider(scroll, "Warm-up Messages",
                     self.v_warmup_count, 0, 20)
        _make_slider(scroll, "Warm-up Extra Delay (secs)",
                     self.v_warmup_delay, 0, 180)

        sw = ctk.CTkSwitch(scroll,
                           text="Use Fixed Delay (no randomization)",
                           variable=self.v_fixed_delay)
        sw.pack(anchor="w", padx=16, pady=12)

        # Presets
        ctk.CTkLabel(scroll, text="Quick Presets",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(16, 6))
        prow = ctk.CTkFrame(scroll, fg_color="transparent")
        prow.pack(fill="x", padx=16, pady=(0, 16))
        for txt, col, name in [
            ("🐢 Safe (Recommended)", "#16A34A", "safe"),
            ("⚡ Moderate", "#D97706", "moderate"),
            ("🚀 Fast (Risky)", "#DC2626", "fast"),
            ("⏱️ Fixed 3 min", "#7C3AED", "fixed3"),
        ]:
            ctk.CTkButton(
                prow, text=txt, fg_color=col, width=0,
                command=lambda n=name: self._apply_preset(n)
            ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    # ═════════════════════════════════════════════════════════════════════════
    # VIEW: ANTI-BAN
    # ═════════════════════════════════════════════════════════════════════════
    def _build_antiban(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._views["antiban"] = f
        f.grid_rowconfigure(3, weight=1)
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f, text="🛡️  Anti-Ban Settings",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 12))

        # ── Info banner ───────────────────────────────────────────────────────
        banner = ctk.CTkFrame(f, fg_color="#1E3A5F")
        banner.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(
            banner,
            text="Bot otomatis PAUSE setelah N pesan sukses untuk menghindari blok WhatsApp.\n"
                 "Progress selalu disimpan sebelum pause — aman tutup & resume kapan saja.",
            text_color="#93C5FD", wraplength=800, justify="left"
        ).pack(padx=16, pady=10)

        # ── Pause limit ───────────────────────────────────────────────────────
        lim_f = ctk.CTkFrame(f)
        lim_f.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        lim_f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(lim_f, text="Pause setelah N pesan sukses:",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 6))

        lim_row = ctk.CTkFrame(lim_f, fg_color="transparent")
        lim_row.grid(row=1, column=0, columnspan=2, sticky="ew",
                     padx=16, pady=(0, 8))
        lim_row.grid_columnconfigure(1, weight=1)

        self._lbl_pause_val = ctk.CTkLabel(
            lim_row, text=f"{self.v_pause_limit.get()} pesan",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#EF4444")
        self._lbl_pause_val.grid(row=0, column=0, padx=(0, 12))

        sl_lim = ctk.CTkSlider(
            lim_row, from_=5, to=200, variable=self.v_pause_limit,
            command=lambda v: self._lbl_pause_val.configure(
                text=f"{int(v)} pesan"))
        sl_lim.grid(row=0, column=1, sticky="ew")

        # Preset buttons
        preset_row = ctk.CTkFrame(lim_f, fg_color="transparent")
        preset_row.grid(row=2, column=0, columnspan=2, sticky="ew",
                        padx=16, pady=(0, 12))
        ctk.CTkLabel(preset_row, text="Preset:").pack(side="left", padx=(0, 8))
        for txt, val in [("30 Aman", 30), ("45 Default", 45),
                         ("60 Moderate", 60), ("100 Berani", 100)]:
            ctk.CTkButton(
                preset_row, text=txt, width=0,
                fg_color="#475569", hover_color="#334155",
                command=lambda v=val: self.v_pause_limit.set(v)
            ).pack(side="left", padx=(0, 6))

        # ── Auto-resume ───────────────────────────────────────────────────────
        res_f = ctk.CTkFrame(f)
        res_f.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(res_f, text="Auto-Resume setelah Pause",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 6))

        sw_row = ctk.CTkFrame(res_f, fg_color="transparent")
        sw_row.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkSwitch(sw_row, text="Aktifkan Auto-Resume",
                      variable=self.v_auto_resume).pack(side="left")

        om_res = ctk.CTkOptionMenu(
            sw_row,
            values=["3 jam (Recommended)", "24 jam (Reset limit WA)",
                    "Manual (tidak auto)"],
            command=self._on_resume_choice)
        om_res.pack(side="left", padx=(20, 0))
        om_res.set("3 jam (Recommended)")

        # ── Status panel ──────────────────────────────────────────────────────
        stat_f = ctk.CTkFrame(f, fg_color="#1C1C2E")
        stat_f.grid(row=4, column=0, sticky="ew", pady=(0, 0))

        self._lbl_ab_status = ctk.CTkLabel(
            stat_f, text="⬤  Idle",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280")
        self._lbl_ab_status.pack(pady=(14, 4))

        self._lbl_ab_countdown = ctk.CTkLabel(
            stat_f, text="",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#F97316")
        self._lbl_ab_countdown.pack(pady=(0, 6))

        self._lbl_ab_info = ctk.CTkLabel(
            stat_f, text=f"Akan pause setiap {self.v_pause_limit.get()} pesan sukses.",
            text_color="#9CA3AF")
        self._lbl_ab_info.pack(pady=(0, 8))

        self._btn_ab_resume = ctk.CTkButton(
            stat_f, text="▶  Resume Sekarang", height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#16A34A", hover_color="#15803D",
            command=self._manual_resume, state="disabled")
        self._btn_ab_resume.pack(pady=(0, 16))

    # ═════════════════════════════════════════════════════════════════════════
    # VIEW: SETTINGS
    # ═════════════════════════════════════════════════════════════════════════
    def _build_settings(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._views["settings"] = f

        ctk.CTkLabel(f, text="⚙️  Settings",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", pady=(0, 16))

        info_f = ctk.CTkFrame(f, fg_color="#1E1E2E")
        info_f.pack(fill="x", pady=(0, 16))
        info = (
            "• Chrome session disimpan otomatis — QR scan hanya sekali.\n"
            "• Progress blast tersimpan di progress_gui.json — aman restart app.\n"
            "• Untuk build .exe: jalankan scripts\\build_exe.bat\n"
            "• Untuk install dependencies baru: scripts\\setup_venv.bat"
        )
        ctk.CTkLabel(info_f, text=info, justify="left",
                     text_color="#93C5FD").pack(padx=16, pady=12)

        # Reset progress button
        ctk.CTkButton(
            f, text="🗑️  Delete Saved Progress",
            fg_color="#7F1D1D", hover_color="#991B1B",
            command=self._delete_progress
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkButton(
            f, text="📄  Export Failed Numbers",
            fg_color="#475569", hover_color="#334155",
            command=self._export_failed
        ).pack(anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    # VIEW NAVIGATION
    # ─────────────────────────────────────────────────────────────────────────
    _NAV_MAP = {
        "dash":     "📊 Dashboard",
        "campaign": "📁 Campaign",
        "delay":    "⏱️ Delay",
        "antiban":  "🛡️ Anti-Ban",
        "settings": "⚙️ Settings",
    }

    def _show_view(self, key: str):
        for k, frame in self._views.items():
            if k == key:
                frame.grid()
            else:
                frame.grid_remove()
        # Update sidebar highlights
        for k, btn_label in self._NAV_MAP.items():
            btn = self._nav_buttons.get(btn_label)
            if btn:
                if k == key:
                    btn.configure(fg_color=("#3B82F6", "#1D4ED8"))
                else:
                    btn.configure(fg_color=("gray75", "gray25"))

    def _show_dashboard(self): self._show_view("dash")
    def _show_campaign(self):  self._show_view("campaign")
    def _show_delay(self):     self._show_view("delay")
    def _show_antiban(self):   self._show_view("antiban")
    def _show_settings(self):  self._show_view("settings")

    # ─────────────────────────────────────────────────────────────────────────
    # FILE OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _toggle_input_mode(self):
        """Switch between file browser and URL input."""
        if self._v_input_mode.get() == "url":
            self._file_input_row.pack_forget()
            self._url_input_row.pack(fill="x", padx=16, pady=(0, 4))
            self._lbl_url_help.pack(anchor="w", padx=16, pady=(0, 8))
        else:
            self._url_input_row.pack_forget()
            self._lbl_url_help.pack_forget()
            self._file_input_row.pack(fill="x", padx=16, pady=(0, 8))

    @staticmethod
    def _sheets_url_to_csv(url: str) -> str:
        """
        Convert a Google Sheets share URL to a direct CSV export URL.
        Supports:
          - https://docs.google.com/spreadsheets/d/{ID}/edit...
          - https://docs.google.com/spreadsheets/d/{ID}/pub...
        Returns the export URL, or raises ValueError if not a valid Sheets URL.
        """
        import re
        m = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
        if not m:
            raise ValueError(
                "Bukan link Google Sheets yang valid.\n\n"
                "Format yang benar:\n"
                "https://docs.google.com/spreadsheets/d/{ID}/edit"
            )
        sheet_id = m.group(1)
        # Preserve gid (sheet tab) if present
        gid_match = re.search(r'[#&?]gid=(\d+)', url)
        gid_param = f"&gid={gid_match.group(1)}" if gid_match else ""
        return (f"https://docs.google.com/spreadsheets/d/{sheet_id}"
                f"/export?format=csv{gid_param}")

    @staticmethod
    def _fetch_sheets_csv(csv_url: str):
        """
        Fetch a Google Sheets CSV export URL and return a pandas DataFrame.
        Uses requests with a browser User-Agent so Google doesn't redirect to
        a login/warning page. Falls back to the gviz endpoint if needed.
        Raises an exception with a descriptive message on failure.
        """
        import re
        import io
        import pandas as pd

        HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/csv,text/plain,*/*",
        }

        def _try_url(url):
            try:
                import requests
            except ImportError:
                raise RuntimeError(
                    "Modul 'requests' tidak terinstall.\n"
                    "Jalankan:  pip install requests")

            resp = requests.get(url, headers=HEADERS,
                                allow_redirects=True, timeout=30)
            resp.raise_for_status()

            ct = resp.headers.get("Content-Type", "")
            if "html" in ct.lower():
                # Google sent a login redirect or warning page
                return None
            if not resp.content.strip():
                return None

            return pd.read_csv(io.StringIO(resp.content.decode("utf-8")))

        # Try primary export URL
        df = _try_url(csv_url)
        if df is not None:
            return df

        # Fallback: gviz endpoint (sometimes works when /export doesn't)
        m = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', csv_url)
        if m:
            gviz_url = (
                f"https://docs.google.com/spreadsheets/d/{m.group(1)}"
                f"/gviz/tq?tqx=out:csv"
            )
            df = _try_url(gviz_url)
            if df is not None:
                return df

        raise RuntimeError(
            "Google mengembalikan halaman HTML bukan CSV.\n\n"
            "Kemungkinan penyebab:\n"
            "• Sheet belum di-share 'Anyone with the link can view'\n"
            "• Sheet memerlukan login Google\n"
            "• Sheet kosong\n\n"
            "Solusi: Buka Google Sheets → Share → "
            "Change to 'Anyone with the link' → Done"
        )

    def _browse_file(self):
        fn = filedialog.askopenfilename(
            title="Select Excel or CSV file",
            filetypes=[("Excel files", "*.xlsx *.xls"),
                       ("CSV files", "*.csv"), ("All files", "*.*")])
        if fn:
            self._v_filepath.set(fn)

    def _load_file(self):
        import pandas as pd

        mode = self._v_input_mode.get()

        # ── URL mode ─────────────────────────────────────────────────────────
        if mode == "url":
            raw_url = self._v_sheets_url.get().strip()
            if not raw_url:
                messagebox.showwarning("Warning",
                    "Paste link Google Sheets terlebih dahulu.")
                return
            try:
                csv_url = self._sheets_url_to_csv(raw_url)
            except ValueError as e:
                messagebox.showerror("Invalid URL", str(e))
                return
            try:
                self.df = self._fetch_sheets_csv(csv_url)
                source_label = "Google Sheets"
            except Exception as e:
                messagebox.showerror(
                    "Gagal Fetch",
                    f"Tidak bisa membaca spreadsheet.\n\n"
                    f"Pastikan:\n"
                    f"• Sheet sudah di-share ke 'Anyone with the link can view'\n"
                    f"• Internet aktif\n\n"
                    f"Error detail:\n{e}")
                return

        # ── File mode ─────────────────────────────────────────────────────────
        else:
            fp = self._v_filepath.get()
            if not fp:
                messagebox.showwarning("Warning", "Please select a file first!")
                return
            try:
                self.df = data_processor.process_spreadsheet(fp)
                source_label = Path(fp).name
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                return

        # ── Common: preview + column mapping ─────────────────────────────────
        try:
            self._refresh_preview()
            cols = [""] + self.df.columns.tolist()
            self._om_phone.configure(values=cols)
            self._om_name.configure(values=cols)
            self._om_message.configure(values=cols)
            # Auto-detect columns
            for c in self.df.columns:
                cl = c.lower()
                if any(x in cl for x in config.PHONE_COLUMN_PATTERNS):
                    self._om_phone.set(c)
                elif any(x in cl for x in config.NAME_COLUMN_PATTERNS):
                    self._om_name.set(c)
                elif any(x in cl for x in config.MESSAGE_COLUMN_PATTERNS):
                    self._om_message.set(c)
            messagebox.showinfo("Loaded",
                f"✅ {len(self.df)} rows loaded from {source_label}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process data:\n{str(e)}")

    def _refresh_preview(self):
        for w in self._preview_scroll.winfo_children():
            w.destroy()
        if self.df is None or self.df.empty:
            return
        cols = self.df.columns.tolist()
        for ci, col in enumerate(cols):
            ctk.CTkLabel(self._preview_scroll, text=str(col),
                         font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=ci, padx=6, pady=4, sticky="ew")
        for ri, (_, row) in enumerate(self.df.head(5).iterrows()):
            for ci, col in enumerate(cols):
                val = str(row[col])
                if len(val) > 22: val = val[:19] + "…"
                ctk.CTkLabel(self._preview_scroll, text=val).grid(
                    row=ri + 1, column=ci, padx=6, pady=2, sticky="ew")

    # ─────────────────────────────────────────────────────────────────────────
    # DELAY PRESETS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_preset(self, name: str):
        P = {
            "safe":   (60, 10, 20, 5, 90,  False),
            "moderate": (45, 5, 15, 3, 60,  False),
            "fast":   (30, 3, 10, 2, 30,   False),
            "fixed3": (180, 0, 0, 0,  0,    True),
        }
        if name in P:
            b, jn, jx, wc, wd, fix = P[name]
            self.v_base_delay.set(b); self.v_jitter_min.set(jn)
            self.v_jitter_max.set(jx); self.v_warmup_count.set(wc)
            self.v_warmup_delay.set(wd); self.v_fixed_delay.set(fix)
            messagebox.showinfo("Preset", f"Applied preset: {name.upper()}")

    # ─────────────────────────────────────────────────────────────────────────
    # AUTO-RESUME CHOICE
    # ─────────────────────────────────────────────────────────────────────────
    def _on_resume_choice(self, sel: str):
        if "3" in sel:
            self.v_resume_hours.set(3); self.v_auto_resume.set(True)
        elif "24" in sel:
            self.v_resume_hours.set(24); self.v_auto_resume.set(True)
        else:
            self.v_auto_resume.set(False)

    # ─────────────────────────────────────────────────────────────────────────
    # PROGRESS SAVE / LOAD
    # ─────────────────────────────────────────────────────────────────────────
    def _save_progress(self, success: int, failed: int):
        try:
            data = {
                "file_name": Path(self._v_filepath.get()).name
                             if self._v_filepath.get() else "Unknown",
                "contacts": self.contacts,
                "current_index": self.current_index,
                "success_count": success,
                "failed_count": failed,
                "failed_contacts": self.failed_contacts,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.progress_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except Exception as e:
            self._log(f"⚠️ Progress save error: {e}")

    def _check_resume_on_startup(self):
        if not self.progress_file.exists():
            return
        try:
            with open(self.progress_file, "r", encoding="utf-8") as fh:
                p = json.load(fh)
            contacts = p.get("contacts", [])
            idx = p.get("current_index", 0)
            if contacts and idx < len(contacts):
                ans = messagebox.askyesno(
                    "Resume Previous Session?",
                    f"Found saved progress:\n\n"
                    f"File: {p.get('file_name', '?')}\n"
                    f"Progress: {idx}/{len(contacts)}\n"
                    f"Success: {p.get('success_count', 0)}\n"
                    f"Failed: {p.get('failed_count', 0)}\n\n"
                    "Resume from where you left off?"
                )
                if ans:
                    self.contacts = contacts
                    self.current_index = idx
                    self.failed_contacts = p.get("failed_contacts", [])
                    self._lbl_remaining.configure(
                        text=str(len(contacts) - idx))
                    self._lbl_success.configure(
                        text=str(p.get("success_count", 0)))
                    self._lbl_failed.configure(
                        text=str(p.get("failed_count", 0)))
                    self._log(f"Loaded progress: resume from index {idx}")
                else:
                    self.progress_file.unlink(missing_ok=True)
        except Exception as e:
            self._log(f"Progress load error: {e}")

    def _delete_progress(self):
        if self.progress_file.exists():
            self.progress_file.unlink(missing_ok=True)
            messagebox.showinfo("Done", "Saved progress deleted.")
        else:
            messagebox.showinfo("Info", "No saved progress found.")

    # ─────────────────────────────────────────────────────────────────────────
    # CAMPAIGN CONTROL
    # ─────────────────────────────────────────────────────────────────────────
    def _start_campaign(self):
        # If no contacts loaded yet (fresh start, not from resume)
        if not self.contacts:
            if self.df is None:
                messagebox.showerror("Error",
                    "Please load a contact file in the Campaign tab first!")
                return
            phone_col = self._om_phone.get()
            if not phone_col:
                messagebox.showerror("Error",
                    "Please select the Phone Column in the Campaign tab!")
                return
            mapping = {
                "phone":   phone_col,
                "name":    self._om_name.get() or None,
                "message": self._om_message.get() or None,
            }
            default_msg = self._txt_default_msg.get("1.0", "end").strip()
            try:
                self.contacts = data_processor.prepare_contacts(
                    self.df, mapping, default_msg)
            except Exception as e:
                messagebox.showerror("Error",
                    f"Failed to prepare contacts:\n{str(e)}")
                return
            if not self.contacts:
                messagebox.showerror("Error", "No valid contacts found!")
                return
            self.current_index = 0
            self.failed_contacts = []

        remaining = len(self.contacts) - self.current_index
        if not messagebox.askyesno(
            "Confirm Start",
            f"Ready to send {remaining} messages.\n\n"
            f"Base delay: {self.v_base_delay.get()}s  |  "
            f"Auto-pause at: {self.v_pause_limit.get()} successes\n\n"
            "Proceed?"
        ):
            return

        self.is_running = True
        self.is_paused = False
        self._session_success = 0
        self._btn_start.configure(state="disabled")
        self._btn_pause.configure(state="normal")
        self._btn_stop.configure(state="normal")
        self._lbl_remaining.configure(text=str(remaining))

        self._show_dashboard()
        threading.Thread(target=self._run_bot, daemon=True).start()

    def _toggle_pause(self):
        if self.is_paused:
            # Resume
            self._auto_resume_cancel.set()
            self.is_paused = False
            self._btn_pause.configure(text="⏸  PAUSE", fg_color="#D97706")
            self._lbl_ab_status.configure(text="⬤  Running", text_color="#22C55E")
            self._lbl_ab_countdown.configure(text="")
            self._btn_ab_resume.configure(state="disabled")
            self._log("▶️ RESUMED")
        else:
            # Pause
            self.is_paused = True
            self._btn_pause.configure(text="▶  RESUME", fg_color="#16A34A")
            self._lbl_countdown.configure(text="PAUSED")
            self._log("⏸️ PAUSED — click Resume to continue")
            messagebox.showinfo("Paused", "Bot paused.\nProgress saved. Click Resume to continue.")

    def _stop_campaign(self):
        if messagebox.askyesno("Stop", "Stop sending?\n\nProgress will be saved."):
            self.is_running = False
            self.is_paused = False
            self._log("⏹ Stopping...")

    # ─────────────────────────────────────────────────────────────────────────
    # BOT THREAD
    # ─────────────────────────────────────────────────────────────────────────
    def _run_bot(self):
        try:
            self._log("=" * 56)
            self._log("🚀 Starting AutoBlast...")
            self._log("=" * 56)

            if not self.driver:
                self._log("Initializing Chrome WebDriver…")
                self.driver = setup_driver()
                self._log("Loading WhatsApp Web…")
                wait_for_whatsapp_load(self.driver)
                self._log("✅ WhatsApp Web loaded!")

            success_count = 0
            failed_count  = len(self.failed_contacts)
            total = len(self.contacts)
            self._session_success = 0

            for idx in range(self.current_index, total):
                if not self.is_running:
                    self._log("⏹ Stopped."); break

                # Pause gate
                while self.is_paused and self.is_running:
                    time_module.sleep(0.5)
                if not self.is_running: break

                contact = self.contacts[idx]
                self.current_index = idx
                num = idx + 1

                self.after(0, self._lbl_next.configure,
                           {"text": f"Sending to: {contact['name']} ({contact['phone']})"})
                self._log(f"\n[{num}/{total}] → {contact['name']} ({contact['phone']})")

                ok = send_message(self.driver, contact["phone"],
                                  contact["message"], contact["name"])

                if ok:
                    success_count += 1
                    self._session_success += 1
                    self._log(f"  ✅ Sent")
                else:
                    failed_count += 1
                    self.failed_contacts.append({
                        "phone": contact["phone"], "name": contact["name"],
                        "reason": "Send failed",
                        "timestamp": datetime.now().isoformat()
                    })
                    self._log(f"  ❌ Failed")

                # Update stat cards
                self.after(0, self._lbl_remaining.configure,
                           {"text": str(total - num)})
                self.after(0, self._lbl_success.configure,
                           {"text": str(success_count)})
                self.after(0, self._lbl_failed.configure,
                           {"text": str(failed_count)})

                # ── AUTO-PAUSE CHECK ──────────────────────────────────────
                limit = self.v_pause_limit.get()
                if (limit > 0
                        and self._session_success > 0
                        and self._session_success % limit == 0
                        and idx < total - 1):

                    # 1. Save progress FIRST
                    self._save_progress(success_count, failed_count)

                    # 2. Pause
                    self.is_paused = True
                    self._log("")
                    self._log("=" * 56)
                    self._log(f"⛔ AUTO-PAUSE: {limit} successful messages reached!")
                    self._log("Progress saved. Resume manually or wait for auto-resume.")
                    self._log("=" * 56)

                    self.after(0, self._lbl_countdown.configure,
                               {"text": "AUTO-PAUSE"})
                    self.after(0, self._btn_pause.configure,
                               {"text": "▶  RESUME", "fg_color": "#16A34A"})
                    self.after(0, self._lbl_ab_status.configure,
                               {"text": f"⛔  PAUSED setelah {limit} sukses",
                                "text_color": "#EF4444"})
                    self.after(0, self._btn_ab_resume.configure,
                               {"state": "normal"})
                    self.after(0, self._lbl_ab_info.configure,
                               {"text": "Progress tersimpan. Resume manual atau tunggu auto-resume."})

                    # 3. Auto-resume countdown
                    if self.v_auto_resume.get():
                        self._auto_resume_cancel.clear()
                        self._auto_resume_thread = threading.Thread(
                            target=self._auto_resume_timer,
                            args=(self.v_resume_hours.get(),),
                            daemon=True)
                        self._auto_resume_thread.start()

                    # 4. Wait while paused
                    while self.is_paused and self.is_running:
                        time_module.sleep(0.5)

                    # 5. Clear auto-pause UI
                    self.after(0, self._lbl_ab_countdown.configure, {"text": ""})
                    self.after(0, self._lbl_ab_status.configure,
                               {"text": "⬤  Running", "text_color": "#22C55E"})
                    self.after(0, self._btn_ab_resume.configure, {"state": "disabled"})
                    if self.is_running:
                        self._log("▶️ RESUMED — continuing…")
                # ─────────────────────────────────────────────────────────

                # Regular progress save
                self._save_progress(success_count, failed_count)

                # Delay between messages
                if idx < total - 1 and self.is_running:
                    if num < total:
                        nxt = self.contacts[num]
                        self.after(0, self._lbl_next.configure,
                                   {"text": f"Next: {nxt['name']} ({nxt['phone']})"})

                    delay = self._calc_delay(num)
                    self._log(f"  ⏳ Waiting {delay:.0f}s…")

                    for rem in range(int(delay), 0, -1):
                        if not self.is_running: break
                        while self.is_paused and self.is_running:
                            time_module.sleep(0.5)
                        if not self.is_running: break
                        mm, ss = rem // 60, rem % 60
                        self.after(0, self._lbl_countdown.configure,
                                   {"text": f"{mm:02d}:{ss:02d}"})
                        time_module.sleep(1)

            # ── Finished ──────────────────────────────────────────────────────
            self._log("\n" + "=" * 56)
            self._log("🎉 COMPLETED!")
            self._log(f"Success: {success_count}  |  Failed: {failed_count}")
            self._log("=" * 56)
            self.after(0, self._lbl_countdown.configure, {"text": "DONE!"})
            self.after(0, self._lbl_next.configure, {"text": "All messages sent."})

            messagebox.showinfo(
                "Campaign Complete",
                f"Finished sending!\n\n"
                f"✅ Success: {success_count}\n❌ Failed: {failed_count}")

            if self.progress_file.exists():
                self.progress_file.unlink(missing_ok=True)

        except Exception as e:
            self._log(f"❌ ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            if self.driver and not self.is_paused:
                self.driver.quit()
                self.driver = None
            self.is_running = False
            self.after(0, self._reset_controls)

    def _calc_delay(self, msg_count: int) -> float:
        delay = float(self.v_base_delay.get())
        if self.v_fixed_delay.get():
            return delay
        if msg_count < self.v_warmup_count.get():
            delay += self.v_warmup_delay.get()
        delay += random.uniform(self.v_jitter_min.get(), self.v_jitter_max.get())
        return delay

    # ─────────────────────────────────────────────────────────────────────────
    # AUTO-RESUME
    # ─────────────────────────────────────────────────────────────────────────
    def _manual_resume(self):
        if self.is_paused:
            self._auto_resume_cancel.set()
            self.is_paused = False
            self.after(0, self._btn_pause.configure,
                       {"text": "⏸  PAUSE", "fg_color": "#D97706"})
            self.after(0, self._lbl_ab_status.configure,
                       {"text": "⬤  Running", "text_color": "#22C55E"})
            self.after(0, self._lbl_ab_countdown.configure, {"text": ""})
            self.after(0, self._btn_ab_resume.configure, {"state": "disabled"})
            self._log("▶️ RESUMED (manual)")

    def _auto_resume_timer(self, hours: float):
        total = int(hours * 3600)
        self._log(f"⏳ Auto-resume in {hours:.0f}h ({total // 60} min)…")
        for rem in range(total, 0, -1):
            if self._auto_resume_cancel.is_set() or not self.is_running:
                return
            h, m, s = rem // 3600, (rem % 3600) // 60, rem % 60
            self.after(0, self._lbl_ab_countdown.configure,
                       {"text": f"{h:02d}:{m:02d}:{s:02d}"})
            time_module.sleep(1)
        if not self._auto_resume_cancel.is_set() and self.is_paused and self.is_running:
            self._log(f"🔔 Auto-resume triggered after {hours:.0f}h!")
            self.after(0, self._manual_resume)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        def _append():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", line)
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
        self.after(0, _append)

    def _reset_controls(self):
        self._btn_start.configure(state="normal")
        self._btn_pause.configure(state="disabled", text="⏸  PAUSE",
                                   fg_color="#D97706")
        self._btn_stop.configure(state="disabled")
        self._lbl_ab_status.configure(text="⬤  Idle", text_color="#6B7280")
        self._lbl_ab_countdown.configure(text="")
        self._btn_ab_resume.configure(state="disabled")
        self._session_success = 0

    def _export_failed(self):
        if not self.failed_contacts:
            messagebox.showinfo("No Failed Numbers",
                                "No failed numbers to export.")
            return
        fn = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"),
                       ("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if fn:
            with open(fn, "w", encoding="utf-8") as fh:
                fh.write("Failed WhatsApp Numbers\n" + "=" * 50 + "\n")
                for c in self.failed_contacts:
                    fh.write(
                        f"{c.get('name','')}\t{c.get('phone','')}\t"
                        f"{c.get('reason','')}\t{c.get('timestamp','')}\n")
            messagebox.showinfo("Exported", f"Saved to:\n{fn}")


# ─── Entry point (for running as module) ──────────────────────────────────────
def main():
    app = AutoBlastApp()
    app.mainloop()


if __name__ == "__main__":
    main()
