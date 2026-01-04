"""
WhatsApp Bot Data Processor
Handles Excel/CSV ingestion, column detection, and phone number sanitization
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from colorama import init, Fore, Style

import config
import utils

# Initialize colorama for Windows
init()

# ============================================================================
# DATA INGESTION
# ============================================================================
def process_spreadsheet(file_path: str) -> pd.DataFrame:
    """
    Read CSV or Excel file with automatic format detection
    
    Args:
        file_path: Path to the spreadsheet file
        
    Returns:
        DataFrame containing the data
        
    Raises:
        ValueError: If file format is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    utils.log_message(f"Reading file: {file_path.name}", "INFO")
    
    # Detect file format and read
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    utils.log_message(f"Loaded {len(df)} rows, {len(df.columns)} columns", "INFO")
    
    return df

# ============================================================================
# COLUMN DETECTION
# ============================================================================
def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Automatically detect which columns contain phone, name, and message
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with detected column names: {'phone': 'col_name', 'name': 'col_name', 'message': 'col_name'}
    """
    detected = {
        'phone': None,
        'name': None,
        'message': None
    }
    
    columns_lower = {col: col.lower() for col in df.columns}
    
    # Detect phone column
    for col, col_lower in columns_lower.items():
        for pattern in config.PHONE_COLUMN_PATTERNS:
            if pattern in col_lower:
                detected['phone'] = col
                break
        if detected['phone']:
            break
    
    # Detect name column
    for col, col_lower in columns_lower.items():
        for pattern in config.NAME_COLUMN_PATTERNS:
            if pattern in col_lower:
                detected['name'] = col
                break
        if detected['name']:
            break
    
    # Detect message column
    for col, col_lower in columns_lower.items():
        for pattern in config.MESSAGE_COLUMN_PATTERNS:
            if pattern in col_lower:
                detected['message'] = col
                break
        if detected['message']:
            break
    
    # Calculate confidence score
    confidence = sum(1 for v in detected.values() if v is not None)
    utils.log_message(f"Auto-detection confidence: {confidence}/3 columns detected", "INFO")
    
    return detected

def preview_data(df: pd.DataFrame, num_rows: int = None):
    """
    Display preview of data with column headers
    
    Args:
        df: DataFrame to preview
        num_rows: Number of rows to show (default from config)
    """
    if num_rows is None:
        num_rows = config.PREVIEW_ROWS
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📋 DATA PREVIEW (First {num_rows} rows){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Display column names with index
    print(f"{Fore.YELLOW}Available Columns:{Style.RESET_ALL}")
    for idx, col in enumerate(df.columns, 1):
        print(f"  {Fore.GREEN}{idx}.{Style.RESET_ALL} {col}")
    
    print(f"\n{Fore.YELLOW}Sample Data:{Style.RESET_ALL}")
    print(df.head(num_rows).to_string(index=False))
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

def interactive_column_selection(df: pd.DataFrame) -> Dict[str, str]:
    """
    Interactive CLI for column selection with auto-detection option
    
    Args:
        df: DataFrame to process
        
    Returns:
        Dictionary with selected column names: {'phone': 'col_name', 'name': 'col_name', 'message': 'col_name'}
    """
    # Show preview
    preview_data(df)
    
    # Auto-detect columns
    detected = detect_columns(df)
    
    # Show auto-detection results
    print(f"{Fore.YELLOW}🤖 Auto-Detection Results:{Style.RESET_ALL}")
    print(f"  Phone column: {Fore.GREEN}{detected['phone'] or 'Not detected'}{Style.RESET_ALL}")
    print(f"  Name column: {Fore.GREEN}{detected['name'] or 'Not detected'}{Style.RESET_ALL}")
    print(f"  Message column: {Fore.GREEN}{detected['message'] or 'Not detected'}{Style.RESET_ALL}")
    print()
    
    # Ask user to confirm or select manually
    if all(detected.values()):
        use_auto = input(f"{Fore.CYAN}Use auto-detected columns? (y/n): {Style.RESET_ALL}").strip().lower()
        if use_auto in ['y', 'yes', 'ya']:
            utils.log_message("Using auto-detected columns", "INFO")
            return detected
    
    # Manual selection
    print(f"\n{Fore.YELLOW}📝 Manual Column Selection{Style.RESET_ALL}")
    selected = {}
    
    # Select phone column
    while True:
        phone_input = input(f"{Fore.CYAN}Enter phone column number or name: {Style.RESET_ALL}").strip()
        phone_col = _parse_column_input(phone_input, df.columns)
        if phone_col:
            selected['phone'] = phone_col
            break
        print(f"{Fore.RED}Invalid column. Please try again.{Style.RESET_ALL}")
    
    # Select name column (optional)
    name_input = input(f"{Fore.CYAN}Enter name column number or name (or press Enter to skip): {Style.RESET_ALL}").strip()
    if name_input:
        name_col = _parse_column_input(name_input, df.columns)
        selected['name'] = name_col if name_col else None
    else:
        selected['name'] = None
    
    # Select message column (optional)
    message_input = input(f"{Fore.CYAN}Enter message column number or name (or press Enter to skip): {Style.RESET_ALL}").strip()
    if message_input:
        message_col = _parse_column_input(message_input, df.columns)
        selected['message'] = message_col if message_col else None
    else:
        selected['message'] = None
    
    utils.log_message(f"Manual selection: {selected}", "INFO")
    return selected

def _parse_column_input(user_input: str, columns: List[str]) -> Optional[str]:
    """
    Parse user input as column number or name
    
    Args:
        user_input: User's input
        columns: List of available columns
        
    Returns:
        Column name or None if invalid
    """
    # Try as number
    try:
        idx = int(user_input) - 1
        if 0 <= idx < len(columns):
            return columns[idx]
    except ValueError:
        pass
    
    # Try as column name
    if user_input in columns:
        return user_input
    
    return None

# ============================================================================
# PHONE NUMBER SANITIZATION
# ============================================================================
def clean_number(phone: str, default_country_code: str = None) -> Optional[str]:
    """
    Clean and normalize phone number with country code
    
    Args:
        phone: Raw phone number
        default_country_code: Default country code (default from config)
        
    Returns:
        Cleaned phone number or None if invalid
    """
    if pd.isna(phone) or not phone:
        return None
    
    phone = str(phone).strip()
    
    if default_country_code is None:
        default_country_code = config.DEFAULT_COUNTRY_CODE
    
    # First, try to extract from wa.me link
    extracted = utils.extract_phone_from_link(phone)
    if extracted:
        phone = extracted
    
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    if not phone:
        return None
    
    # Remove leading zeros
    phone = phone.lstrip('0')
    
    # Add country code if not present
    if not phone.startswith(default_country_code):
        phone = default_country_code + phone
    
    # Validate
    if utils.validate_phone_number(phone):
        return phone
    
    return None

def parse_wa_link(text: str) -> Optional[str]:
    """
    Extract and clean phone number from WhatsApp link
    
    Args:
        text: Text containing wa.me link or phone parameter
        
    Returns:
        Cleaned phone number or None
    """
    extracted = utils.extract_phone_from_link(text)
    if extracted:
        return clean_number(extracted)
    return None

# ============================================================================
# DATA PREPARATION
# ============================================================================
def prepare_contacts(df: pd.DataFrame, column_mapping: Dict[str, str], default_message: str = None) -> List[Dict[str, str]]:
    """
    Prepare contact list with cleaned phone numbers
    
    Args:
        df: DataFrame with contact data
        column_mapping: Column mapping from interactive_column_selection
        default_message: Default message if message column not specified
        
    Returns:
        List of contact dictionaries
    """
    contacts = []
    
    phone_col = column_mapping['phone']
    name_col = column_mapping.get('name')
    message_col = column_mapping.get('message')
    
    utils.log_message(f"Preparing contacts from {len(df)} rows...", "INFO")
    
    for idx, row in df.iterrows():
        # Clean phone number
        phone = clean_number(row[phone_col])
        
        if not phone:
            utils.log_message(f"Row {idx+1}: Invalid phone number '{row[phone_col]}'", "WARNING")
            continue
        
        # Get name
        name = utils.clean_string(row[name_col]) if name_col and name_col in row else "Customer"
        
        # Get message
        if message_col and message_col in row:
            message = utils.clean_string(row[message_col])
        else:
            message = default_message or "Hello!"
        
        contacts.append({
            'phone': phone,
            'name': name,
            'message': message,
            'original_row': idx + 1
        })
    
    utils.log_message(f"Prepared {len(contacts)} valid contacts", "INFO")
    
    return contacts
