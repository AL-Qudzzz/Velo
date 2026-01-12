"""
Velo Bot Utility Functions
Helper functions for timing, logging, progress tracking, and validation
"""

import json
import random
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from . import config

# ============================================================================
# TIMING UTILITIES
# ============================================================================
def calculate_delay(message_count: int) -> float:
    """
    Calculate delay with randomized jitter and warm-up strategy
    
    Args:
        message_count: Number of messages sent so far
        
    Returns:
        Delay in seconds
    """
    # Base delay
    delay = config.BASE_DELAY
    
    # Add warm-up delay for first N messages
    if message_count < config.WARMUP_COUNT:
        delay += config.WARMUP_DELAY
    
    # Add randomized jitter
    jitter = random.uniform(config.JITTER_MIN, config.JITTER_MAX)
    delay += jitter
    
    return delay

def human_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """
    Add a small random delay to simulate human behavior
    
    Args:
        min_seconds: Minimum delay
        max_seconds: Maximum delay
    """
    time.sleep(random.uniform(min_seconds, max_seconds))

# ============================================================================
# LOGGING UTILITIES
# ============================================================================
def log_message(message: str, level: str = "INFO"):
    """
    Log a message with timestamp to both console and file
    
    Args:
        message: Message to log
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime(config.LOG_DATE_FORMAT)
    log_entry = f"{timestamp} - {level} - {message}"
    
    # Print to console with color
    color_codes = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
    }
    reset_code = "\033[0m"
    
    colored_entry = f"{color_codes.get(level, '')}{log_entry}{reset_code}"
    print(colored_entry)
    
    # Write to log file
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

# ============================================================================
# PROGRESS TRACKING
# ============================================================================
def save_progress(data: Dict[str, Any]):
    """
    Save progress to JSON file for resume capability
    
    Args:
        data: Progress data to save
    """
    try:
        with open(config.PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_message(f"Progress saved: {data.get('processed', 0)}/{data.get('total', 0)} messages", "DEBUG")
    except Exception as e:
        log_message(f"Failed to save progress: {str(e)}", "ERROR")

def load_progress() -> Optional[Dict[str, Any]]:
    """
    Load progress from JSON file
    
    Returns:
        Progress data or None if file doesn't exist
    """
    try:
        if config.PROGRESS_FILE.exists():
            with open(config.PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            log_message(f"Progress loaded: {data.get('processed', 0)}/{data.get('total', 0)} messages", "INFO")
            return data
    except Exception as e:
        log_message(f"Failed to load progress: {str(e)}", "WARNING")
    return None

def clear_progress():
    """Clear progress file"""
    try:
        if config.PROGRESS_FILE.exists():
            config.PROGRESS_FILE.unlink()
            log_message("Progress file cleared", "DEBUG")
    except Exception as e:
        log_message(f"Failed to clear progress: {str(e)}", "WARNING")

# ============================================================================
# PHONE NUMBER VALIDATION
# ============================================================================
def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Check if matches valid pattern
    pattern = re.compile(config.VALID_PHONE_PATTERN)
    return bool(pattern.match(phone))

def extract_phone_from_link(text: str) -> Optional[str]:
    """
    Extract phone number from wa.me link or phone= parameter
    
    Args:
        text: Text that might contain a WhatsApp link
        
    Returns:
        Extracted phone number or None
    """
    if not text:
        return None
    
    text = str(text).strip()
    
    # Try each regex pattern
    for pattern in config.PHONE_REGEX_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None

# ============================================================================
# STRING UTILITIES
# ============================================================================
def clean_string(text: str) -> str:
    """
    Clean and normalize string
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)

# ============================================================================
# CONFIRMATION UTILITIES
# ============================================================================
def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation
    
    Args:
        message: Confirmation message
        
    Returns:
        True if confirmed, False otherwise
    """
    response = input(f"{message} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'ya']

def display_summary(total: int, estimated_time: float):
    """
    Display summary before starting
    
    Args:
        total: Total number of messages
        estimated_time: Estimated time in seconds
    """
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total messages to send: {total}")
    print(f"Estimated time: {format_duration(estimated_time)}")
    print(f"Base delay: {config.BASE_DELAY}s + jitter ({config.JITTER_MIN}-{config.JITTER_MAX}s)")
    print(f"Warm-up messages: {config.WARMUP_COUNT} (with +{config.WARMUP_DELAY}s delay)")
    print("="*60 + "\n")
