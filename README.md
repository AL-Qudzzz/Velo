# Velo Bot - WhatsApp Automation Tool

A Python-based automation tool for sending bulk WhatsApp messages through WhatsApp Web. Built with **Selenium** for reliable browser automation and ships with a full-featured **GUI** (Tkinter) as well as a CLI interface.

---

## 📥 Download

> **Ready-to-use installer — no Python required!**
>
> [**⬇ Download VeloBot Setup v1.0.0**](https://www.mediafire.com/file/g9mg98eshwjfo5e/VeloBot_Setup_v1.0.exe/file)
> [**⬇ Download VeloBot Setup v2.1.0**](https://www.mediafire.com/file/dkazoudyhggvafw/VeloBot_Setup_v2.1.exe/file)
>
> Run the installer and follow the on-screen instructions. Google Chrome must be installed on your system.

---

## Features

### Core Automation

- **Automated message sending** via WhatsApp Web using Selenium & Chrome WebDriver
- **Session persistence** — scan the QR code once; the session is stored in `whatsapp_session/` for reuse
- **Intelligent phone number parsing** — supports `08xxx`, `628xxx`, `+628xxx`, `wa.me/` links, and full WhatsApp API URLs
- **WhatsApp URL message extraction** — automatically extracts the message body from `api.whatsapp.com/send?phone=...&text=...` URLs

### Data Import

- **Excel & CSV support** — import `.xlsx`, `.xls`, and `.csv` files
- **Auto-detect columns** — the tool recognizes common column names for phone, name, and message (e.g. `phone`, `nomor`, `nama`, `message`, `pesan`, etc.)
- **Data preview** — see the first 5 rows of your file before sending

### GUI (Graphical User Interface)

- **Three-tab layout** — _File & Columns_, _Delay Settings_, and _Execution_
- **File browser** — pick your Excel/CSV file with a native file dialog
- **Interactive column mapping** — dropdown selectors for Phone, Name (optional), and Message (optional) columns
- **Default message editor** — define a fallback message used when no per-row message is provided
- **Delay Configuration panel** with sliders for Base Delay, Jitter Min/Max, Warm-up Count, and Warm-up Extra Delay
- **Quick presets** — _Safe (Recommended)_, _Moderate_, _Fast (Risky)_, and _Fixed 3 min_
- **Fixed delay mode** — lock in an exact interval with no randomization
- **Estimated time calculator** — instantly see how long the entire batch will take
- **Real-time countdown timer** — a large `MM:SS` display shows the remaining wait between messages
- **Progress bar & statistics dashboard** — live Success / Failed / Remaining counters
- **Pause / Resume** — temporarily halt and continue without losing your place
- **Stop** — gracefully abort the session; progress is saved automatically
- **Resume on startup** — when you reopen the app, it detects unfinished sessions and asks to resume
- **Export failed numbers** — save a list of contacts that could not be reached to a `.txt` or `.csv` file
- **Execution log** — scrollable real-time log of every action and error

### CLI (Command Line Interface)

- Same core automation accessible from the terminal
- Suitable for scripting or headless server environments

### Distribution

- **Build to Windows executable (.exe)** for easy distribution (no Python required on target machine)

---

## Requirements

| Requirement             | Minimum Version |
| ----------------------- | --------------- |
| Python                  | 3.8+            |
| Google Chrome           | Latest stable   |
| Active WhatsApp account | —               |

> **Note:** If you are running the pre-built `.exe`, Python is **not** required.

---

## Setup (For Developers)

1. **Clone or download** this repository:

   ```bash
   git clone https://github.com/your-org/Velo.git
   cd Velo
   ```

2. **Run the automated setup script** — it creates a virtual environment and installs all dependencies:

   ```bash
   scripts\setup_venv.bat
   ```

   This script will:
   - Create a Python virtual environment (`.venv`)
   - Activate the virtual environment
   - Install every package listed in `requirements.txt`:

     | Package             | Purpose                           |
     | ------------------- | --------------------------------- |
     | `selenium`          | Browser automation                |
     | `pandas`            | Data processing                   |
     | `openpyxl`          | Excel file support                |
     | `webdriver-manager` | Automatic ChromeDriver management |
     | `colorama`          | Colored CLI output                |
     | `pyperclip`         | Clipboard-based message pasting   |

3. **Verify** the installation by launching the GUI:

   ```bash
   scripts\run_gui.bat
   ```

   The _Automatic Blasting WA_ window should appear.

---

## Running Velo Bot — GUI Mode (Step-by-Step)

Below is a complete walkthrough from importing your CSV/Excel file to finishing a blasting session.

### Step 1 — Launch the Application

```bash
scripts\run_gui.bat
```

Or, if you are using the pre-built executable:

```
Double-click  AutoBlast.exe
```

The main window will open with three tabs at the top: **📁 File & Columns**, **⏱️ Delay Settings**, and **▶️ Execution**.

> **Resume prompt:** If a previous session was interrupted, a dialog will appear asking _"Do you want to resume?"_. Click **Yes** to continue from where you left off, or **No** to start fresh.

---

### Step 2 — Import Your CSV / Excel File (Tab: 📁 File & Columns)

1. Click the **Browse** button.
2. In the file dialog, select your `.csv`, `.xlsx`, or `.xls` file.  
   The file path will appear in the text field.
3. Click the **Load File** button.
4. A **Data Preview** panel will display the first 5 rows of your file so you can verify the data.

#### Prepare Your File

Your file should contain **at least** a column with phone numbers. Name and message columns are optional.

| Phone        | Name       | Message                       |
| ------------ | ---------- | ----------------------------- |
| 08123456789  | John Doe   | Hello, this is a test message |
| 628234567890 | Jane Smith | Custom message here           |

**Supported phone number formats:**

| Format           | Example                                                         |
| ---------------- | --------------------------------------------------------------- |
| Local Indonesian | `08123456789`                                                   |
| International    | `628123456789` , `+628123456789`                                |
| wa.me link       | `https://wa.me/628123456789`                                    |
| WhatsApp API URL | `https://api.whatsapp.com/send?phone=628xxx&text=Hello%20there` |

> **Tip:** If your phone column contains WhatsApp API URLs with a `text=` parameter, the message will be **automatically extracted** — no need for a separate message column.

---

### Step 3 — Map the Columns

After loading the file, map each dropdown to the correct column:

| Dropdown           | What to Select                                                 | Required?   |
| ------------------ | -------------------------------------------------------------- | ----------- |
| **Phone Column**   | The column that contains phone numbers or wa.me links          | ✅ Yes      |
| **Name Column**    | The column with contact names (used in logs / personalization) | ❌ Optional |
| **Message Column** | The column with per-contact messages                           | ❌ Optional |

- **Auto-Detect:** Click the **Auto-Detect Columns** button (orange) and the tool will attempt to match columns automatically based on common naming patterns.
- **Default Message:** If you did not select a Message column, or some rows are blank, the **Default Message** text box at the bottom is used as the fallback. Edit it to your desired text.

---

### Step 4 — Configure Delay Settings (Tab: ⏱️ Delay Settings)

Switch to the **⏱️ Delay Settings** tab. This is where you control the timing between messages to stay under WhatsApp's radar.

#### Option A — Use a Quick Preset

Click one of the preset buttons:

| Preset                    | Base Delay | Jitter  | Warm-up             | Risk Level  |
| ------------------------- | ---------- | ------- | ------------------- | ----------- |
| 🐢 **Safe (Recommended)** | 60 s       | 10–20 s | 5 msgs × 90 s extra | Low         |
| ⚡ **Moderate**           | 45 s       | 5–15 s  | 3 msgs × 60 s extra | Medium      |
| 🚀 **Fast (Risky)**       | 30 s       | 3–10 s  | 2 msgs × 30 s extra | High        |
| ⏱️ **Fixed 3 min**        | 180 s      | 0       | None                | Low (Fixed) |

#### Option B — Custom Configuration

Use the sliders to set each value manually:

| Slider                  | Description                                           | Range    |
| ----------------------- | ----------------------------------------------------- | -------- |
| **Base Delay**          | Minimum wait between messages                         | 30–300 s |
| **Jitter Min**          | Minimum random extra seconds                          | 0–30 s   |
| **Jitter Max**          | Maximum random extra seconds                          | 0–60 s   |
| **Warm-up Messages**    | How many initial messages use the extra warm-up delay | 0–20     |
| **Warm-up Extra Delay** | Additional seconds added during the warm-up phase     | 0–180 s  |

#### Fixed Delay Mode

Check **🔒 Use Fixed Delay (no randomization)** to disable jitter entirely. The bot will wait **exactly** the Base Delay value between every message — useful when you need predictable timing.

#### Estimated Time

The **📊 Estimated Time** display at the bottom updates live as you adjust the sliders, showing how long it will take to process all loaded contacts (e.g., _"For 150 messages: ~2h 30m"_).

---

### Step 5 — Start Blasting (Tab: ▶️ Execution)

Switch to the **▶️ Execution** tab, then:

1. Click **▶️ Start Sending**.
2. A **confirmation dialog** will appear showing:
   - Number of messages to send
   - Base delay and delay mode (Fixed / Variable)
3. Click **Yes** to proceed.

#### What Happens Next

1. **Chrome opens automatically** via Selenium.
2. **WhatsApp Web loads.** If this is your first time (or the session expired), you will need to **scan the QR code** with your phone's WhatsApp app. The bot waits until WhatsApp is fully loaded.
3. The bot begins sending messages one by one. For each contact:
   - The contact's name and phone number appear in the _"Sending to:"_ label.
   - The message is sent through WhatsApp Web.
   - The result (✓ success / ✗ failed) is written to the **Execution Log**.
4. After each message, a **countdown timer** (`MM:SS`) counts down the delay before the next message.
5. The **progress bar** and **statistics** (Success / Failed / Remaining) update in real time.

---

### Step 6 — Pause, Resume, or Stop

During execution you have full control:

| Button        | Action                                                                             |
| ------------- | ---------------------------------------------------------------------------------- |
| **⏸️ Pause**  | Temporarily halts sending. Progress is saved. The button changes to **▶️ Resume**. |
| **▶️ Resume** | Continues from the exact point where you paused.                                   |
| **⏹️ Stop**   | Gracefully stops the session. Progress is saved so you can resume later.           |

> **Closing the app while running?** No worries — when you relaunch, the app detects the saved progress and offers to resume.

---

### Step 7 — Review Results & Export Failed Numbers

Once all messages are processed (or after stopping):

- A **completion dialog** shows the total Success and Failed counts.
- The **Statistics** panel at the bottom displays the final numbers.
- If any messages failed, click **📄 Export Failed Numbers** to save them:
  1. Choose a save location and file name (`.txt` or `.csv`).
  2. The exported file lists each failed phone number, contact name, failure reason, and timestamp.
  3. Use this file to clean your contact list or retry later.

---

## CLI Mode

For command-line usage without the GUI:

```bash
scripts\run_cli.bat
```

Or run directly with a specific file:

```bash
python -m src.whatsapp_bot path\to\your\file.xlsx
```

---

## Building Windows Executable

Want to distribute this app to users without Python? Build it as a Windows `.exe`:

| Method      | Command                 | Description                                         |
| ----------- | ----------------------- | --------------------------------------------------- |
| GUI Builder | `scripts\build_gui.bat` | Launches **auto-py-to-exe** with a visual interface |
| CLI Builder | `scripts\build_exe.bat` | Automated build with **PyInstaller**                |

For complete build instructions, see [BUILD_GUIDE.md](docs/BUILD_GUIDE.md).

---

## Project Structure

```
AutoBlast/
├── src/                        # Source code
│   ├── config.py              # Configuration (delays, XPaths, paths)
│   ├── utils.py               # Utility functions
│   ├── data_processor.py      # Excel/CSV data handling & column detection
│   ├── whatsapp_bot.py        # Core Selenium automation (CLI)
│   └── whatsapp_bot_gui.py    # Tkinter GUI application
├── scripts/                    # Launcher & build scripts
│   ├── setup_venv.bat         # Create virtual env & install deps
│   ├── run_gui.bat            # Launch GUI mode
│   ├── run_cli.bat            # Launch CLI mode
│   ├── build_gui.bat          # Build .exe (GUI method)
│   └── build_exe.bat          # Build .exe (CLI method)
├── docs/                       # Documentation
│   ├── BUILD_GUIDE.md
│   ├── USER_INSTALLATION_GUIDE.md
│   ├── GUI_GUIDE.md
│   ├── GUI_ENHANCED_FEATURES.md
│   ├── URL_EXTRACTION_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── INSTALLER_GUIDE.md
│   └── TUTORIAL_INNO_SETUP.md
├── tests/                      # Test files
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── whatsapp_session/           # Chrome session data (auto-created)
```

---

## Troubleshooting

| Problem                               | Solution                                                                                                                           |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **QR Code not appearing**             | Ensure Chrome is installed and up-to-date. Check your internet connection. Delete the `whatsapp_session/` folder and try again.    |
| **Messages sent as multiple bubbles** | Install `pyperclip` (`pip install pyperclip`). The tool uses clipboard paste to send complete messages in a single bubble.         |
| **"Invalid number" errors**           | Verify phone numbers include the country code. Remove special characters except `+`. Confirm the number is registered on WhatsApp. |
| **Bot detected / account banned**     | Increase delay settings. Use the _Safe_ preset. Reduce daily message volume. Add more randomization (jitter).                      |

---

## Important Notes

### ⚠️ Account Safety

- This tool automates WhatsApp Web, which may violate WhatsApp's Terms of Service.
- **Use at your own risk.**
- Start with small batches to test.
- Avoid sending spam or unsolicited messages.
- Respect WhatsApp's usage limits.

### ✅ Best Practices

- Always test with a small group first.
- Use realistic delays (**60+ seconds** recommended).
- Personalize messages whenever possible.
- Monitor for any warnings from WhatsApp.

---

## Support

For issues or questions, check the documentation in the `docs/` folder:

| Document                     | Description                      |
| ---------------------------- | -------------------------------- |
| `ARCHITECTURE.md`            | Technical architecture details   |
| `BUILD_GUIDE.md`             | How to build the Windows `.exe`  |
| `GUI_GUIDE.md`               | Complete GUI walkthrough         |
| `GUI_ENHANCED_FEATURES.md`   | Advanced GUI features            |
| `URL_EXTRACTION_GUIDE.md`    | WhatsApp URL message extraction  |
| `USER_INSTALLATION_GUIDE.md` | End-user installation guide      |
| `INSTALLER_GUIDE.md`         | Windows installer guide          |
| `TUTORIAL_INNO_SETUP.md`     | Step-by-step Inno Setup tutorial |
