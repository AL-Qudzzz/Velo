"""
WhatsApp Bot Main Automation Module
Selenium-based automation for WhatsApp Web message broadcasting
"""

import time
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config
import utils
import data_processor

# ============================================================================
# SELENIUM DRIVER SETUP
# ============================================================================
def setup_driver() -> webdriver.Chrome:
    """
    Initialize Selenium WebDriver with Chrome and session persistence
    
    Returns:
        Configured Chrome WebDriver instance
    """
    utils.log_message("Initializing Chrome WebDriver...", "INFO")
    
    # Chrome options
    options = webdriver.ChromeOptions()
    
    # Session persistence - critical for avoiding repeated QR scans
    session_path = config.get_session_path()
    options.add_argument(f"user-data-dir={session_path}")
    
    # User agent
    options.add_argument(f"user-agent={config.USER_AGENT}")
    
    # Window size
    options.add_argument(f"--window-size={config.CHROME_WINDOW_SIZE}")
    
    # Disable automation flags (appear more human-like)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Disable notifications
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    # Headless mode (optional, not recommended for WhatsApp)
    if config.CHROME_HEADLESS:
        options.add_argument("--headless")
        utils.log_message("Running in headless mode", "WARNING")
    
    # Initialize driver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set timeouts
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    
    utils.log_message("Chrome WebDriver initialized successfully", "INFO")
    
    return driver

# ============================================================================
# WHATSAPP WEB INITIALIZATION
# ============================================================================
def wait_for_whatsapp_load(driver: webdriver.Chrome, timeout: int = None):
    """
    Wait for WhatsApp Web to fully load (QR scan or auto-login)
    
    Args:
        driver: Chrome WebDriver instance
        timeout: Maximum wait time in seconds
    """
    if timeout is None:
        timeout = config.PAGE_LOAD_TIMEOUT
    
    utils.log_message("Loading WhatsApp Web...", "INFO")
    driver.get("https://web.whatsapp.com")
    
    # Wait for either QR code or chat panel (indicating logged in)
    wait = WebDriverWait(driver, timeout)
    
    try:
        # Check if QR code is present
        qr_element = driver.find_elements(By.XPATH, config.XPATH_QR_CODE)
        
        if qr_element:
            utils.log_message("QR Code detected. Please scan with your phone...", "INFO")
            print(f"\n{'='*60}")
            print("📱 SCAN QR CODE")
            print("="*60)
            print("Please scan the QR code in the browser window with WhatsApp")
            print("on your phone. Waiting for login...")
            print(f"{'='*60}\n")
        
        # Wait for chat panel to appear (login successful)
        wait.until(EC.presence_of_element_located((By.XPATH, config.XPATH_CHAT_LOADED)))
        utils.log_message("WhatsApp Web loaded successfully!", "INFO")
        
        # Additional wait for full initialization
        time.sleep(3)
        
    except TimeoutException:
        utils.log_message("Timeout waiting for WhatsApp Web to load", "ERROR")
        raise

# ============================================================================
# MESSAGE SENDING
# ============================================================================
def send_message(driver: webdriver.Chrome, phone: str, message: str, name: str = "Customer") -> bool:
    """
    Send a message to a WhatsApp number
    
    Args:
        driver: Chrome WebDriver instance
        phone: Phone number (with country code, no +)
        message: Message text to send
        name: Contact name (for logging)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Navigate to chat via wa.me link
        url = f"https://web.whatsapp.com/send?phone={phone}"
        utils.log_message(f"Opening chat for {name} ({phone})...", "INFO")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Check for invalid number popup
        if detect_invalid_number(driver):
            utils.log_message(f"Invalid WhatsApp number: {phone}", "WARNING")
            return False
        
        # Wait for message box
        wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
        message_box = wait.until(
            EC.presence_of_element_located((By.XPATH, config.XPATH_MESSAGE_BOX))
        )
        
        # Human-like delay before typing
        utils.human_delay(0.5, 1.5)
        
        # Click on message box
        message_box.click()
        
        # Try to use clipboard paste method (preferred - sends as single bubble)
        try:
            import pyperclip
            
            # Copy message to clipboard
            pyperclip.copy(message)
            
            # Paste using Ctrl+V (works on both Windows and Linux)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            
            # Small delay to ensure paste completes
            time.sleep(0.5)
            
        except ImportError:
            # Fallback: Use Shift+Enter for newlines (if pyperclip not available)
            utils.log_message("pyperclip not available, using Shift+Enter method", "WARNING")
            
            # Split message by newlines and send with Shift+Enter
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                # Add Shift+Enter for newline (except for last line)
                if i < len(lines) - 1:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        
        # Human-like delay before sending
        utils.human_delay(0.5, 1.0)
        
        # Send message (Enter key)
        message_box.send_keys(Keys.ENTER)
        
        # Wait for message to be sent
        time.sleep(2)
        
        utils.log_message(f"✓ Message sent to {name} ({phone})", "INFO")
        return True
        
    except TimeoutException:
        utils.log_message(f"Timeout sending message to {phone}", "ERROR")
        return False
    except Exception as e:
        utils.log_message(f"Error sending message to {phone}: {str(e)}", "ERROR")
        return False

def detect_invalid_number(driver: webdriver.Chrome) -> bool:
    """
    Detect if WhatsApp shows invalid number popup
    
    Args:
        driver: Chrome WebDriver instance
        
    Returns:
        True if invalid number detected, False otherwise
    """
    try:
        # Wait briefly for popup
        time.sleep(1)
        
        # Check for invalid number message
        invalid_elements = driver.find_elements(By.XPATH, config.XPATH_INVALID_NUMBER)
        if invalid_elements:
            return True
        
        # Check alternative popup
        invalid_alt = driver.find_elements(By.XPATH, config.XPATH_INVALID_NUMBER_ALT)
        if invalid_alt:
            # Check if popup contains error text
            popup_text = invalid_alt[0].text.lower()
            if 'invalid' in popup_text or 'tidak valid' in popup_text:
                return True
        
        return False
        
    except Exception:
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Main execution function"""
    
    print(f"\n{'='*60}")
    print("🤖 WhatsApp Bot Blasting System")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to Excel/CSV file: ").strip()
    
    try:
        # Load spreadsheet
        df = data_processor.process_spreadsheet(input_file)
        
        # Interactive column selection
        column_mapping = data_processor.interactive_column_selection(df)
        
        # Get default message if no message column
        default_message = None
        if not column_mapping.get('message'):
            default_message = input("\nEnter default message to send: ").strip()
        
        # Prepare contacts
        contacts = data_processor.prepare_contacts(df, column_mapping, default_message)
        
        if not contacts:
            utils.log_message("No valid contacts found!", "ERROR")
            return
        
        # Safety check
        if len(contacts) > config.MAX_MESSAGES_PER_SESSION:
            utils.log_message(f"Warning: {len(contacts)} contacts exceeds safety limit of {config.MAX_MESSAGES_PER_SESSION}", "WARNING")
            if not utils.confirm_action("Continue anyway?"):
                return
        
        # Calculate estimated time
        avg_delay = config.BASE_DELAY + (config.JITTER_MIN + config.JITTER_MAX) / 2
        warmup_extra = config.WARMUP_DELAY * min(len(contacts), config.WARMUP_COUNT)
        estimated_time = (avg_delay * len(contacts)) + warmup_extra
        
        # Display summary
        utils.display_summary(len(contacts), estimated_time)
        
        # Confirm start
        if config.REQUIRE_CONFIRMATION:
            if not utils.confirm_action("Start sending messages?"):
                utils.log_message("Operation cancelled by user", "INFO")
                return
        
        # Check for existing progress
        progress = utils.load_progress()
        start_index = 0
        
        if progress and progress.get('file') == input_file:
            if utils.confirm_action(f"Resume from message {progress.get('processed', 0) + 1}?"):
                start_index = progress.get('processed', 0)
        else:
            utils.clear_progress()
        
        # Initialize driver
        driver = setup_driver()
        
        try:
            # Load WhatsApp Web
            wait_for_whatsapp_load(driver)
            
            # Send messages
            success_count = 0
            failed_count = 0
            
            for idx, contact in enumerate(contacts[start_index:], start=start_index):
                message_num = idx + 1
                
                utils.log_message(f"\n[{message_num}/{len(contacts)}] Processing {contact['name']}...", "INFO")
                
                # Send message
                success = send_message(
                    driver,
                    contact['phone'],
                    contact['message'],
                    contact['name']
                )
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Save progress
                utils.save_progress({
                    'file': input_file,
                    'total': len(contacts),
                    'processed': message_num,
                    'success': success_count,
                    'failed': failed_count,
                    'last_update': datetime.now().isoformat()
                })
                
                # Calculate and apply delay (except for last message)
                if message_num < len(contacts):
                    delay = utils.calculate_delay(message_num)
                    utils.log_message(f"Waiting {delay:.1f}s before next message...", "DEBUG")
                    time.sleep(delay)
            
            # Final summary
            print(f"\n{'='*60}")
            print("✅ COMPLETED")
            print("="*60)
            print(f"Total messages: {len(contacts)}")
            print(f"Successful: {success_count}")
            print(f"Failed: {failed_count}")
            print(f"{'='*60}\n")
            
            # Clear progress on successful completion
            utils.clear_progress()
            
        finally:
            # Close driver
            utils.log_message("Closing browser...", "INFO")
            driver.quit()
    
    except KeyboardInterrupt:
        utils.log_message("\n\nOperation interrupted by user", "WARNING")
        print("\nProgress has been saved. Run again to resume.")
    except Exception as e:
        utils.log_message(f"Fatal error: {str(e)}", "ERROR")
        raise

if __name__ == "__main__":
    main()
