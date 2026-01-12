# AutoBlast - WhatsApp Automation Tool

A Python-based automation tool for sending bulk WhatsApp messages through WhatsApp Web. Built with Selenium for reliable browser automation and includes both CLI and GUI interfaces.

## Features

- Automated message sending via WhatsApp Web
- Support for Excel (.xlsx, .xls) and CSV file formats
- Intelligent column detection for phone numbers, names, and messages
- Session persistence (scan QR code once)
- Customizable delay settings to avoid detection
- Message extraction from WhatsApp API URLs
- Progress tracking and resume capability
- Real-time countdown timer
- Failed number logging and export
- Pause/resume functionality

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- Active WhatsApp account

## Installation

1. Clone or download this repository

2. Run the setup script to create virtual environment and install dependencies:

```bash
scripts\setup_venv.bat
```

This will automatically:

- Create a Python virtual environment
- Install all required packages
- Set up the project structure

## Usage

### GUI Mode (Recommended)

Run the graphical interface:

```bash
scripts\run_gui.bat
```

The GUI provides:

- File browser for selecting Excel/CSV files
- Interactive column mapping
- Visual delay configuration with presets
- Real-time progress monitoring
- Countdown timer for next message
- Statistics dashboard

### CLI Mode

For command-line usage:

```bash
scripts\run_cli.bat
```

Or with a specific file:

```bash
python -m src.whatsapp_bot path\to\your\file.xlsx
```

## File Format

Your Excel or CSV file should contain:

| Phone        | Name       | Message                       |
| ------------ | ---------- | ----------------------------- |
| 08123456789  | John Doe   | Hello, this is a test message |
| 628234567890 | Jane Smith | Custom message here           |

Supported phone number formats:

- Indonesian: 08xxx, 628xxx, +628xxx
- WhatsApp links: https://wa.me/628xxx
- WhatsApp API URLs with embedded messages

The tool will automatically detect column names like "phone", "number", "nama", "name", "message", "pesan", etc.

## Configuration

### Delay Settings

Adjust timing in the GUI or modify `src/config.py`:

- **Base Delay**: Time between messages (default: 60 seconds)
- **Jitter**: Random variation to appear more human-like
- **Warm-up**: Extra delay for first few messages
- **Fixed Mode**: Use exact delay without randomization

Recommended settings:

- Safe: 60s base + 10-20s jitter
- Moderate: 45s base + 5-15s jitter
- Fast: 30s base + 3-10s jitter (higher risk)

### Session Data

WhatsApp session is stored in `whatsapp_session/` directory. Delete this folder to reset and scan QR code again.

## Advanced Features

### WhatsApp URL Message Extraction

The tool can extract messages directly from WhatsApp API URLs:

```
https://api.whatsapp.com/send?phone=628xxx&text=Your%20message%20here
```

Simply paste these URLs in the phone column, and the message will be automatically extracted. No need to fill the message column separately.

### Pause and Resume

In GUI mode:

- Click "Pause" to temporarily stop sending
- Progress is automatically saved
- Click "Resume" to continue from where you left off
- Close and reopen the application - it will ask if you want to resume

### Failed Numbers Export

After completion, export a list of failed numbers:

- Click "Export Failed Numbers" button
- Choose save location
- Review and retry failed contacts

## Project Structure

```
AutoBlast/
├── src/                    # Source code
│   ├── config.py          # Configuration settings
│   ├── utils.py           # Utility functions
│   ├── data_processor.py  # Data handling
│   ├── whatsapp_bot.py    # Core automation (CLI)
│   └── whatsapp_bot_gui.py # GUI application
├── scripts/               # Launcher scripts
├── docs/                  # Documentation
├── tests/                 # Test files
└── whatsapp_session/      # Session data
```

## Troubleshooting

**QR Code not appearing**

- Make sure Chrome is installed
- Check your internet connection
- Delete `whatsapp_session/` folder and try again

**Messages sent as multiple bubbles**

- Ensure `pyperclip` is installed: `pip install pyperclip`
- The tool uses clipboard paste to send complete messages

**"Invalid number" errors**

- Verify phone numbers include country code
- Remove any special characters except + and numbers
- Check if the number is registered on WhatsApp

**Bot detected/banned**

- Increase delay settings
- Use "Safe" preset
- Reduce daily message volume
- Add more randomization (jitter)

## Important Notes

**Account Safety**

- This tool automates WhatsApp Web, which may violate WhatsApp's Terms of Service
- Use at your own risk
- Start with small batches to test
- Avoid sending spam or unsolicited messages
- Respect WhatsApp's usage limits

**Best Practices**

- Always test with a small group first
- Use realistic delays (60+ seconds recommended)
- Don't send identical messages to everyone
- Personalize messages when possible
- Monitor for any warnings from WhatsApp

## Support

For issues or questions, please check the documentation in the `docs/` folder:

- `ARCHITECTURE.md` - Technical details
- `GUI_GUIDE.md` - Complete GUI walkthrough
- `URL_EXTRACTION_GUIDE.md` - URL message extraction
- `GUI_ENHANCED_FEATURES.md` - Advanced features
