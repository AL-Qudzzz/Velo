## WhatsApp URL Message Extraction Feature

### 🎯 Overview

The bot can now automatically extract pre-formatted messages from WhatsApp API URLs! This means you don't need to type messages manually - just paste the WhatsApp URL and the bot will extract both the phone number and the complete message.

### 📋 Supported URL Formats

**Format 1: Full WhatsApp API URL**

```
https://api.whatsapp.com/send?phone=6289637412604&text=Hello%20World
```

**Format 2: Short wa.me URL with text**

```
https://wa.me/6289637412604?text=Hello%20World
```

**Format 3: URL-encoded messages (with special characters)**

```
https://api.whatsapp.com/send?phone=6289637412604&text=Hello%2C%20this%20is%20a%20test!%0ALine%202%0ALine%203
```

### ✨ How It Works

1. **Automatic Detection**: When you load an Excel file, the bot checks if the phone column contains WhatsApp URLs
2. **Message Extraction**: If a URL contains a `text=` parameter, the bot extracts and decodes it
3. **Priority System**:
   - **Highest**: Message from URL
   - **Medium**: Message from Excel column
   - **Lowest**: Default message

### 📊 Excel File Format

Create an Excel file with WhatsApp URLs in the phone column:

| WhatsApp_URL                                                       | Name       |
| ------------------------------------------------------------------ | ---------- |
| https://api.whatsapp.com/send?phone=628123456789&text=Hello%20John | John Doe   |
| https://wa.me/628234567890?text=Hi%20Jane                          | Jane Smith |
| 08345678901                                                        | Bob Wilson |

**Notes:**

- Row 1-2: Bot extracts message from URL
- Row 3: No URL message, uses default message

### 🚀 Usage Example

**Step 1: Prepare Excel with URLs**

```
Column: WhatsApp_URL
Row 1: https://api.whatsapp.com/send?phone=6289637412604&text=Halloo%2C%20kak%20NAUFAL...
Row 2: https://api.whatsapp.com/send?phone=6281234567890&text=Dear%20customer...
```

**Step 2: Run the bot**

```bash
python whatsapp_bot.py your_file.xlsx
```

**Step 3: Select columns**

- Phone column: WhatsApp_URL
- Name column: Name (optional)
- Message column: (leave empty or press Enter)

**Step 4: Bot automatically extracts messages**

```
[1/2] Processing NAUFAL...
✓ Using message from WhatsApp URL
✓ Message sent to NAUFAL (6289637412604)
```

### 🔧 Technical Details

**URL Decoding:**

- `%20` → space
- `%2C` → comma
- `%0A` → newline
- `%3A` → colon
- And all other URL-encoded characters

**Message Extraction:**

```python
# Example URL
url = "https://api.whatsapp.com/send?phone=628123456789&text=Hello%20World"

# Extracted data
{
    'phone': '628123456789',
    'message': 'Hello World'
}
```

### 💡 Use Cases

**1. Bulk messaging with pre-formatted templates**

- Create URLs with formatted messages
- Include newlines, special characters
- Maintain consistent formatting

**2. Multi-language campaigns**

- Each URL has message in specific language
- No need to manage separate message columns

**3. Personalized messages**

- Generate URLs with personalized content
- Include recipient-specific information

**4. Template reuse**

- Save URLs with common message templates
- Quick campaign setup

### ⚠️ Important Notes

1. **URL Encoding**: Messages must be URL-encoded

   - Use online tools or Python's `urllib.parse.quote()`
   - Example: `Hello World` → `Hello%20World`

2. **Newlines**: Use `%0A` for line breaks

   - Example: `Line 1%0ALine 2`

3. **Special Characters**: Must be encoded

   - Comma: `%2C`
   - Colon: `%3A`
   - Question mark: `%3F`

4. **Mixed Formats**: You can mix URLs and plain numbers
   - URLs: Message extracted from URL
   - Plain numbers: Use default message

### 🧪 Testing

Run the test script to verify:

```bash
python test_url_extraction.py
```

This will:

1. Test URL parsing with your example
2. Create `sample_with_urls.xlsx` with various formats
3. Show extracted messages

### 📝 Example: Real-World Usage

**Scenario**: Send Tracer Study invitation to alumni

**Excel File:**

```
WhatsApp_URL: https://api.whatsapp.com/send?phone=6289637412604&text=Halloo%2C%20kak%20NAUFAL%20IMAM%20HIDAYATULLAH%0AAlumni%20UIN%20Syarif%20Hidayatullah%20Jakarta...
Name: NAUFAL IMAM HIDAYATULLAH
```

**Result:**

```
Extracted message:
---
Halloo, kak NAUFAL IMAM HIDAYATULLAH
Alumni UIN Syarif Hidayatullah Jakarta
Angkatan Wisuda 131

Assalamualaikum Wr.Wb.
Dengan hormat, kami tim Pusat Karier UIN Jakarta...
[Full message with proper formatting]
---
```

### 🎯 Benefits

✅ **No manual typing**: Copy-paste URLs directly
✅ **Preserve formatting**: Newlines and special characters maintained
✅ **Faster setup**: No need to create separate message column
✅ **Template reuse**: Save URLs for future campaigns
✅ **Error reduction**: No typos from manual entry

---

**Feature Status**: ✅ Fully Implemented  
**Version**: 1.1  
**Added**: 2026-01-06
