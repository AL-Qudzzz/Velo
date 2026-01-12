"""
Test script for WhatsApp URL message extraction feature
Demonstrates how the bot can extract messages from WhatsApp API URLs
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import data_processor

def test_url_extraction():
    """Test URL message extraction"""
    
    print("="*80)
    print("Testing WhatsApp URL Message Extraction")
    print("="*80)
    print()
    
    # Test URL from user's example
    test_url = """https://api.whatsapp.com/send?phone=6289637412604&text=Halloo%2C%20kak%20NAUFAL%20IMAM%20HIDAYATULLAH%0AAlumni%20UIN%20Syarif%20Hidayatullah%20Jakarta%0AAngkatan%20Wisuda%20131%0A%0AAssalamualaikum%20Wr.Wb.%20%0ADengan%20hormat%2C%20kami%20tim%20Pusat%20Karier%20UIN%20Jakarta%20mengundang%20Anda%20untuk%20berpartisipasi%20dalam%20penyelenggaraan%20Tracer%20Study%20UIN%20Jakarta%202025%20dengan%20mengisi%20survei%20karier%20alumni%20guna%20membantu%20mengevaluasi%20dan%20meningkatkan%20kualitas%20pendidikan%20UIN%20Syarif%20Hidayatullah%20Jakarta.%0A%20%0ABerikut%20merupakan%20langkah-langkah%20untuk%20berpartisipasi%20dalam%20TS%20UIN%20Jakarta%202025.%0ATutorial%20Pengisian%3A%0A1.%20Buka%20Google%20Form%20TS%20Pusat%20Karier%20UIN%20Jakarta%20dengan%20mengakses%20link%20berikut%3A%20https%3A%2F%2Fs.id%2FTSUINJKT2025%0A2.%20Kemudian%2C%20silahkan%20mengisi%20seluruh%20pertanyaan%20dan%20klik%20%E2%80%98Kirim%27%0A3.%20Jika%20ada%20pertanyaan%2C%20silahkan%20berkabar%20melalui%20chat%20WA%20ini%0A%0AAtas%20perhatian%20dan%20partisipasi%20anda%2C%20kami%20ucapkan%20terima%20kasih.%20Semoga%2C%20keberkahan%20dan%20perlindungan%20Allah%20SWT%20selalu%20menyertai%20perjalanan%20karier%20anda.%0A%0ASalam%20Hangat%0A%28Pusat%20Karier%20UIN%20Jakarta%29%0A%0AMengetahui%0AM.%20Kholis%20Hamdy%0A%0AKepala%20Pusat%20Karier%20UIN%20Jakarta"""
    
    print("Test 1: Extract message from URL")
    print("-" * 80)
    message = data_processor.extract_message_from_url(test_url)
    
    if message:
        print("✓ Message extracted successfully!")
        print(f"\nMessage length: {len(message)} characters")
        print(f"\nFirst 200 characters:")
        print(message[:200] + "...")
        print(f"\nFull message:")
        print(message)
    else:
        print("✗ Failed to extract message")
    
    print("\n" + "="*80)
    print("\nTest 2: Parse complete WhatsApp URL")
    print("-" * 80)
    
    parsed = data_processor.parse_whatsapp_url(test_url)
    
    if parsed:
        print("✓ URL parsed successfully!")
        print(f"\nPhone: {parsed.get('phone', 'Not found')}")
        print(f"Message length: {len(parsed.get('message', ''))} characters")
        print(f"\nMessage preview:")
        print(parsed.get('message', '')[:200] + "...")
    else:
        print("✗ Failed to parse URL")
    
    print("\n" + "="*80)

def create_sample_with_urls():
    """Create sample Excel file with WhatsApp URLs"""
    
    print("\n" + "="*80)
    print("Creating Sample Excel with WhatsApp URLs")
    print("="*80)
    print()
    
    # Sample data with different formats
    data = {
        'WhatsApp_URL': [
            # Format 1: Full URL with message
            'https://api.whatsapp.com/send?phone=628123456789&text=Hello%20John%2C%20this%20is%20a%20test%20message!',
            
            # Format 2: wa.me with message
            'https://wa.me/628234567890?text=Hi%20Jane%2C%20how%20are%20you%3F',
            
            # Format 3: Full URL with long message (like user's example)
            'https://api.whatsapp.com/send?phone=628345678901&text=Dear%20Bob%2C%0A%0AThis%20is%20a%20multi-line%20message.%0ALine%202%0ALine%203%0A%0AThank%20you!',
            
            # Format 4: Plain phone number (fallback to default message)
            '08456789012',
            
            # Format 5: URL without message (will use default)
            'https://wa.me/628567890123'
        ],
        'Name': [
            'John Doe',
            'Jane Smith',
            'Bob Wilson',
            'Alice Johnson',
            'Charlie Brown'
        ]
    }
    
    df = pd.DataFrame(data)
    
    output_file = Path(__file__).parent / 'sample_with_urls.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"✓ Sample file created: {output_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {', '.join(df.columns)}")
    print()
    print("Sample data preview:")
    print(df.to_string(index=False))
    print()
    print("How to use:")
    print("1. Run the bot: python whatsapp_bot.py sample_with_urls.xlsx")
    print("2. Select 'WhatsApp_URL' as phone column")
    print("3. Select 'Name' as name column")
    print("4. Leave message column empty (or press Enter)")
    print("5. Bot will automatically extract messages from URLs!")

if __name__ == "__main__":
    # Run tests
    test_url_extraction()
    
    # Create sample file
    create_sample_with_urls()
    
    print("\n" + "="*80)
    print("✓ All tests completed!")
    print("="*80)
