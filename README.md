# WhatsApp Bot Blasting System

🤖 **Production-ready WhatsApp automation system** using Python and Selenium WebDriver for automated message broadcasting via web.whatsapp.com.

## ✨ Features

- ✅ **Graphical User Interface (GUI)**: Easy-to-use Tkinter interface with visual controls
- ✅ **WhatsApp URL Message Extraction**: Automatically extract messages from WhatsApp API URLs
- ✅ **Customizable Delays**: Adjust base delay, jitter, and warm-up settings with sliders
- ✅ **Delay Presets**: Quick presets (Safe/Moderate/Fast) for different risk levels
- ✅ **Session Persistence**: QR code scan only once, automatic login on subsequent runs
- ✅ **Interactive Column Selection**: Auto-detect or manually select Excel columns
- ✅ **Smart Phone Sanitization**: Handles wa.me links, country codes, and formatting
- ✅ **Anti-Ban Protection**: Configurable delays with real-time estimates
- ✅ **Warm-up Strategy**: Customizable warm-up message count and delay
- ✅ **Progress Tracking**: Real-time progress bar and statistics (success/failed/remaining)
- ✅ **Invalid Number Detection**: Automatically skips non-existent WhatsApp numbers
- ✅ **Human-like Behavior**: Randomized typing speed and delays

## 📋 Requirements

- Windows 10/11
- Python 3.8 or higher
- Google Chrome browser
- Active WhatsApp account

## 🚀 Quick Start

### 1. Setup Virtual Environment

Run the automated setup script:

```bash
setup_venv.bat
```

This will:

- Create a `.venv` virtual environment
- Install all dependencies
- Verify the installation

### 2. Run the Application

**Option A: GUI Mode (Recommended)**

Double-click `scripts\run_gui.bat` or run:

```bash
scripts\run_gui.bat
```

This launches the graphical interface where you can:

- Browse and load Excel/CSV files
- Preview data and select columns
- Customize delay settings with sliders
- Monitor progress in real-time

**Option B: Command Line Mode**

For advanced users:

```bash
.venv\Scripts\activate
python whatsapp_bot.py contacts.xlsx
```

### 3. Prepare Your Data

Create an Excel file (`.xlsx`) or CSV file with your contacts. Example:

| Phone                      | Name | Message     |
| -------------------------- | ---- | ----------- |
| 08123456789                | John | Hello John! |
| +628234567890              | Jane | Hi Jane!    |
| https://wa.me/628345678901 | Bob  | Hey Bob!    |

**Supported formats:**

- Plain numbers: `08123456789`
- With country code: `+628123456789` or `628123456789`
- WhatsApp links: `https://wa.me/628123456789`

## 🖥️ Using the GUI

### Main Interface

The GUI has 3 tabs:

#### 📁 Tab 1: File & Columns

1. Click **Browse** to select your Excel/CSV file
2. Click **Load File** to preview the data
3. Click **Auto-Detect Columns** or manually select:
   - Phone column (required)
   - Name column (optional)
   - Message column (optional)
4. Enter a default message if no message column is selected

#### ⏱️ Tab 2: Delay Settings

1. Adjust delay settings using sliders:
   - **Base Delay**: Time between messages (30-180s)
   - **Jitter Min/Max**: Random variation (0-60s)
   - **Warm-up Messages**: Number of slower initial messages (0-20)
   - **Warm-up Extra Delay**: Additional delay for warm-up (0-180s)
2. Use **Quick Presets**:
   - 🐢 **Safe (Recommended)**: 60s base + 10-20s jitter
   - ⚡ **Moderate**: 45s base + 5-15s jitter
   - 🚀 **Fast (Risky)**: 30s base + 3-10s jitter
3. View estimated total time for your message batch

#### ▶️ Tab 3: Execution

1. Click **▶️ Start Sending** to begin
2. Scan QR code (first time only)
3. Monitor progress:
   - Progress bar shows completion
   - Real-time log displays each action
   - Statistics show success/failed/remaining counts
4. Click **⏹️ Stop** to interrupt if needed

### 4. Command Line Workflow (Alternative)

The bot will guide you through:

1. **Data Preview**: Shows first 5 rows of your Excel file
2. **Column Detection**: Auto-detects phone, name, and message columns
3. **Column Selection**: Accept auto-detection or manually select columns
4. **Confirmation**: Review summary and confirm before starting
5. **QR Scan** (first time only): Scan QR code with your phone
6. **Automated Sending**: Sit back and let the bot work!

## 📊 Column Selection

### Auto-Detection

The system automatically detects columns containing:

- **Phone**: `phone`, `nomor`, `telepon`, `hp`, `whatsapp`, `wa`, `number`
- **Name**: `name`, `nama`, `customer`, `client`, `contact`
- **Message**: `message`, `pesan`, `text`, `msg`, `content`

### Manual Selection

If auto-detection fails or you prefer manual selection:

```
Available Columns:
  1. Phone Number
  2. Customer Name
  3. Message Text

Enter phone column number or name: 1
Enter name column number or name: 2
Enter message column number or name: 3
```

You can enter either:

- Column number (e.g., `1`)
- Column name (e.g., `Phone Number`)

## ⚙️ Configuration

Edit `config.py` to customize:

### Timing (Anti-Ban)

```python
BASE_DELAY = 60          # Base delay between messages (seconds)
JITTER_MIN = 5           # Minimum random jitter
JITTER_MAX = 15          # Maximum random jitter
WARMUP_COUNT = 5         # Number of warm-up messages
WARMUP_DELAY = 90        # Extra delay for warm-up
```

### Phone Numbers

```python
DEFAULT_COUNTRY_CODE = "62"  # Indonesia (change as needed)
```

### Safety Limits

```python
MAX_MESSAGES_PER_SESSION = 100  # Maximum messages per run
REQUIRE_CONFIRMATION = True      # Ask before starting
```

## 🛡️ Safety Features

### Anti-Ban Strategy

1. **Base Delay**: 60 seconds between messages
2. **Randomized Jitter**: +5 to +15 seconds random variation
3. **Warm-up Period**: First 5 messages sent slower (90s extra delay)
4. **Human-like Typing**: Simulated typing with natural pauses

### Invalid Number Handling

- Automatically detects invalid WhatsApp numbers
- Skips and logs failed numbers
- Continues with remaining contacts

### Progress Tracking

- Auto-saves progress after each message
- Resume capability if interrupted (Ctrl+C)
- Prevents duplicate sends

## 📁 Project Structure

```
AutoBlast/
├── whatsapp_bot.py          # Main automation script
├── config.py                # Configuration settings
├── utils.py                 # Utility functions
├── data_processor.py        # Data ingestion & processing
├── requirements.txt         # Python dependencies
├── setup_venv.bat          # Virtual environment setup
├── README.md               # This file
├── .venv/                  # Virtual environment (created by setup)
├── whatsapp_session/       # Chrome session data (auto-created)
├── progress.json           # Progress tracking (auto-created)
└── bot_log.txt            # Execution logs (auto-created)
```

## 🔧 Troubleshooting

### QR Code Not Appearing

- Make sure Chrome browser is visible (not minimized)
- Check that `CHROME_HEADLESS = False` in `config.py`
- Try deleting `whatsapp_session/` folder and restart

### "Invalid Phone Number" Errors

- Ensure phone numbers include country code
- Check `DEFAULT_COUNTRY_CODE` in `config.py`
- Verify numbers are active WhatsApp accounts

### Messages Not Sending

- Check internet connection
- Verify WhatsApp Web is accessible in browser
- Ensure you're not logged out of WhatsApp
- Check `bot_log.txt` for detailed errors

### Chrome Driver Issues

- Update Chrome to latest version
- Delete `.venv/` and run `setup_venv.bat` again
- Check firewall/antivirus settings

## ⚠️ Important Warnings

### Compliance

> [!CAUTION] > **You are responsible for compliance** with:
>
> - WhatsApp Terms of Service
> - Local regulations (GDPR, TCPA, etc.)
> - Anti-spam laws
> - Recipient consent requirements

### Rate Limiting

> [!WARNING]
> WhatsApp may **ban your number** if you:
>
> - Send too many messages too quickly
> - Send to many invalid numbers
> - Receive many spam reports
>
> **Use responsibly and at your own risk!**

### Best Practices

- ✅ Only message people who opted in
- ✅ Include opt-out instructions
- ✅ Start with small batches (10-20 messages)
- ✅ Monitor for blocks/bans
- ✅ Use business WhatsApp account if possible
- ❌ Don't send spam or unsolicited messages
- ❌ Don't exceed 100 messages per session
- ❌ Don't reduce delays below recommended values

## 📝 Example Usage

### Basic Usage

```bash
python whatsapp_bot.py contacts.xlsx
```

### With Custom Message

If your Excel doesn't have a message column:

```bash
python whatsapp_bot.py contacts.xlsx
# When prompted: "Enter default message to send: Hello! This is a test message."
```

### Resume Interrupted Session

```bash
python whatsapp_bot.py contacts.xlsx
# Bot will ask: "Resume from message 25? (y/n)"
```

## 🤝 Support

For issues or questions:

1. Check `bot_log.txt` for detailed error messages
2. Review this README thoroughly
3. Verify your Excel file format matches examples
4. Test with a small sample (2-3 contacts) first
