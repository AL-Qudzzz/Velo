"""
WhatsApp Bot Configuration Module
Centralized configuration for timing, XPath selectors, and system parameters
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORY PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent.absolute()
SESSION_DIR = BASE_DIR / "whatsapp_session"
PROGRESS_FILE = BASE_DIR / "progress.json"
LOG_FILE = BASE_DIR / "bot_log.txt"

# ============================================================================
# TIMING CONFIGURATION (Anti-Ban Strategy)
# ============================================================================
# Base delay between messages (seconds)
BASE_DELAY = 60

# Randomized jitter range (seconds) - added to base delay
JITTER_MIN = 5
JITTER_MAX = 15

# Warm-up strategy: slower for first N messages
WARMUP_COUNT = 5
WARMUP_DELAY = 90  # Extra delay for warm-up messages

# Timeout values (seconds)
PAGE_LOAD_TIMEOUT = 60
ELEMENT_WAIT_TIMEOUT = 30
MESSAGE_SEND_TIMEOUT = 20

# ============================================================================
# WHATSAPP WEB XPATHS (Robust Relative Selectors)
# ============================================================================
# Main chat search box
XPATH_SEARCH_BOX = '//div[@contenteditable="true"][@data-tab="3"]'

# Message input box
XPATH_MESSAGE_BOX = '//div[@contenteditable="true"][@data-tab="10"]'

# Send button
XPATH_SEND_BUTTON = '//span[@data-icon="send"]'

# Invalid number popup detection
XPATH_INVALID_NUMBER = '//div[contains(text(), "Phone number shared via url is invalid")]'

# Alternative invalid number detection
XPATH_INVALID_NUMBER_ALT = '//div[@data-animate-modal-popup="true"]//div[contains(@class, "popup")]'

# Chat loaded indicator (presence of main chat area)
XPATH_CHAT_LOADED = '//div[@id="pane-side"]'

# QR Code element (for initial login)
XPATH_QR_CODE = '//canvas[@aria-label="Scan me!"]'

# ============================================================================
# PHONE NUMBER CONFIGURATION
# ============================================================================
# Default country code (Indonesia)
DEFAULT_COUNTRY_CODE = "62"

# Phone number regex patterns
PHONE_REGEX_PATTERNS = [
    r'wa\.me/(\d+)',           # wa.me/628123456789
    r'phone=(\d+)',             # phone=628123456789
    r'api\.whatsapp\.com/send\?phone=(\d+)',  # Full WhatsApp API link
]

# Valid phone number pattern (after cleaning)
VALID_PHONE_PATTERN = r'^\d{10,15}$'

# ============================================================================
# DATA PROCESSING CONFIGURATION
# ============================================================================
# Column name patterns for auto-detection
PHONE_COLUMN_PATTERNS = ['phone', 'nomor', 'telepon', 'hp', 'whatsapp', 'wa', 'number', 'mobile']
NAME_COLUMN_PATTERNS = ['name', 'nama', 'customer', 'client', 'contact']
MESSAGE_COLUMN_PATTERNS = ['message', 'pesan', 'text', 'msg', 'content']

# Preview rows for column selection
PREVIEW_ROWS = 5

# ============================================================================
# SELENIUM CONFIGURATION
# ============================================================================
# Chrome options
CHROME_HEADLESS = False  # Set to True for headless mode (not recommended for WhatsApp)
CHROME_WINDOW_SIZE = "1920,1080"

# User agent (to appear more human-like)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ============================================================================
# RETRY AND ERROR HANDLING
# ============================================================================
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# SAFETY LIMITS
# ============================================================================
MAX_MESSAGES_PER_SESSION = 100  # Safety limit to prevent abuse
REQUIRE_CONFIRMATION = True  # Ask for confirmation before starting

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def ensure_directories():
    """Create necessary directories if they don't exist"""
    SESSION_DIR.mkdir(exist_ok=True)
    
def get_session_path():
    """Get the absolute path for Chrome session storage"""
    ensure_directories()
    return str(SESSION_DIR.absolute())
