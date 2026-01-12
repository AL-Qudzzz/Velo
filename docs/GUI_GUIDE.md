# WhatsApp Bot GUI - User Guide

## 🎨 Interface Overview

The WhatsApp Bot GUI provides an intuitive graphical interface for managing your message broadcasting campaigns with full control over timing and execution.

![GUI Interface](https://via.placeholder.com/800x600?text=WhatsApp+Bot+GUI)

## 🚀 Getting Started

### Launch the Application

1. **First time setup**:

   ```bash
   setup_venv.bat
   ```

2. **Launch GUI**:
   ```bash
   run_gui.bat
   ```
   Or double-click `run_gui.bat` in Windows Explorer

## 📋 Tab-by-Tab Guide

### Tab 1: 📁 File & Columns

#### File Selection

1. Click **Browse** button
2. Select your Excel (.xlsx, .xls) or CSV file
3. Click **Load File** to import

#### Data Preview

- View first 5 rows of your data
- Check column names and data format
- Verify phone numbers are present

#### Column Mapping

- **Auto-Detect Columns**: Automatically identifies phone, name, and message columns
- **Manual Selection**: Use dropdowns to select specific columns
  - **Phone Column** (required): Column containing phone numbers
  - **Name Column** (optional): Column containing contact names
  - **Message Column** (optional): Column containing personalized messages
- **Default Message**: Enter a message to use if no message column is selected

**Supported Phone Formats:**

- Plain: `08123456789`
- With country code: `+628123456789` or `628123456789`
- WhatsApp links: `https://wa.me/628123456789`

---

### Tab 2: ⏱️ Delay Settings

#### Delay Configuration Sliders

**Base Delay (30-180 seconds)**

- Primary delay between each message
- Default: 60 seconds
- Higher = safer, lower = riskier

**Jitter Min/Max (0-60 seconds)**

- Random variation added to base delay
- Makes timing appear more human-like
- Default: 5-15 seconds

**Warm-up Messages (0-20)**

- Number of initial messages sent with extra delay
- Helps establish trust with WhatsApp
- Default: 5 messages

**Warm-up Extra Delay (0-180 seconds)**

- Additional delay for warm-up messages only
- Default: 90 seconds

#### Quick Presets

Click a preset button to instantly configure delays:

**🐢 Safe (Recommended)**

- Base: 60s, Jitter: 10-20s
- Warm-up: 5 messages with +90s
- Best for: First-time users, large campaigns
- Risk: Very low

**⚡ Moderate**

- Base: 45s, Jitter: 5-15s
- Warm-up: 3 messages with +60s
- Best for: Experienced users, medium campaigns
- Risk: Low-medium

**🚀 Fast (Risky)**

- Base: 30s, Jitter: 3-10s
- Warm-up: 2 messages with +30s
- Best for: Testing, small batches only
- Risk: High - may trigger bans!

#### Time Estimate

Real-time calculation shows estimated total time for your campaign based on:

- Number of contacts
- Current delay settings
- Warm-up configuration

---

### Tab 3: ▶️ Execution

#### Control Buttons

**▶️ Start Sending**

- Validates your configuration
- Shows confirmation dialog with summary
- Begins message sending process
- Opens Chrome browser with WhatsApp Web

**⏹️ Stop**

- Gracefully stops the bot
- Saves progress
- Allows resuming later

#### Progress Monitoring

**Progress Bar**

- Visual indicator of completion percentage
- Updates after each message

**Message Counter**

- Shows: `X / Y messages sent`
- Updates in real-time

**Statistics**

- **Success**: Messages successfully sent (green)
- **Failed**: Messages that failed (red)
- **Remaining**: Messages left to send (blue)

#### Execution Log

Real-time log showing:

- Timestamp for each action
- File loading status
- Message sending results
- Delay countdowns
- Error messages (if any)

**Log Format:**

```
[14:30:15] Starting WhatsApp Bot...
[14:30:18] Initializing Chrome WebDriver...
[14:30:22] Loading WhatsApp Web...
[14:30:35] WhatsApp Web loaded successfully!
[14:30:36] [1/50] Processing John Doe...
[14:30:40] ✓ Message sent to John Doe (628123456789)
[14:30:40] Waiting 72.3s before next message...
```

---

## 🎯 Step-by-Step Workflow

### Complete Campaign Setup

1. **Launch Application**

   ```bash
   run_gui.bat
   ```

2. **Load Your Data** (Tab 1)

   - Browse and select Excel file
   - Click "Load File"
   - Verify preview shows correct data

3. **Configure Columns** (Tab 1)

   - Click "Auto-Detect Columns"
   - Review detected columns
   - Adjust manually if needed
   - Enter default message if required

4. **Set Delays** (Tab 2)

   - Choose a preset (recommended: Safe)
   - Or customize with sliders
   - Check estimated time
   - Ensure delays are appropriate for your use case

5. **Execute Campaign** (Tab 3)

   - Click "▶️ Start Sending"
   - Review confirmation dialog
   - Click "Yes" to proceed
   - **First time only**: Scan QR code in browser
   - Monitor progress and logs

6. **Monitor & Manage**
   - Watch progress bar advance
   - Check statistics for success/failure rates
   - Review log for any issues
   - Click "⏹️ Stop" if needed

---

## ⚙️ Advanced Features

### Custom Delay Strategies

**Conservative (High Safety)**

```
Base: 90s
Jitter: 15-30s
Warm-up: 10 messages, +120s
Total: ~140-150s per message
```

**Balanced (Medium Safety)**

```
Base: 60s
Jitter: 10-20s
Warm-up: 5 messages, +90s
Total: ~70-80s per message
```

**Aggressive (Low Safety)**

```
Base: 30s
Jitter: 5-10s
Warm-up: 2 messages, +30s
Total: ~35-40s per message
```

### Delay Calculation Formula

```
For warm-up messages (1 to N):
  delay = base_delay + warmup_delay + random(jitter_min, jitter_max)

For normal messages (N+1 onwards):
  delay = base_delay + random(jitter_min, jitter_max)
```

---

## 🛡️ Safety Tips

### Before Starting

✅ **Test First**: Use 2-3 contacts to verify everything works
✅ **Check Numbers**: Ensure all phone numbers are valid
✅ **Review Message**: Check for typos and formatting
✅ **Set Safe Delays**: Start with "Safe" preset
✅ **Monitor Closely**: Watch the first 10 messages

### During Execution

✅ **Don't Close Browser**: Keep Chrome window open
✅ **Stay Connected**: Ensure stable internet
✅ **Watch for Errors**: Check log for red error messages
✅ **Respect Limits**: Don't exceed 100 messages per session

### After Completion

✅ **Review Statistics**: Check success/failure rates
✅ **Check Logs**: Look for patterns in failures
✅ **Monitor WhatsApp**: Ensure account is not restricted
✅ **Adjust Settings**: Increase delays if you had issues

---

## ❓ Troubleshooting

### GUI Won't Launch

**Problem**: Double-clicking `run_gui.bat` shows error
**Solution**:

1. Run `setup_venv.bat` first
2. Check Python is installed: `python --version`
3. Manually activate: `.venv\Scripts\activate` then `python whatsapp_bot_gui.py`

### Auto-Detect Not Working

**Problem**: Auto-detect doesn't find columns
**Solution**:

1. Check column names in preview
2. Manually select from dropdowns
3. Ensure column headers are in first row

### QR Code Not Appearing

**Problem**: Browser opens but no QR code
**Solution**:

1. Wait 10-15 seconds for page to load
2. Check internet connection
3. Try refreshing the page manually
4. Close browser and restart GUI

### Messages Not Sending

**Problem**: Bot starts but messages don't send
**Solution**:

1. Check log for specific errors
2. Verify phone numbers are valid
3. Ensure WhatsApp Web is loaded (green checkmark)
4. Try logging out and scanning QR again

### High Failure Rate

**Problem**: Many messages showing as "Failed"
**Solution**:

1. Increase base delay to 90s
2. Check if numbers are valid WhatsApp accounts
3. Verify message format (no special characters causing issues)
4. Reduce batch size to 20-30 messages

---

## 🎓 Best Practices

### Campaign Planning

1. **Start Small**: Test with 5-10 messages first
2. **Gradual Scaling**: Increase batch size slowly (10 → 25 → 50)
3. **Daily Limits**: Don't exceed 100 messages per day initially
4. **Timing**: Send during business hours (9 AM - 6 PM)
5. **Content**: Keep messages professional and relevant

### Delay Optimization

1. **First Campaign**: Use "Safe" preset (60s + 10-20s jitter)
2. **After Success**: Can reduce to "Moderate" (45s + 5-15s)
3. **Never Go Below**: 30s base delay (high ban risk)
4. **Always Use Jitter**: Randomization is critical
5. **Warm-up Always**: At least 3-5 messages with extra delay

### Data Quality

1. **Clean Data**: Remove duplicates before importing
2. **Valid Numbers**: Verify numbers are active WhatsApp accounts
3. **Formatting**: Use consistent phone number format
4. **Testing**: Send to yourself first to check formatting

---

## 📊 Understanding Statistics

### Success Count (Green)

- Messages successfully delivered
- Confirmed by WhatsApp Web
- Target: >95% success rate

### Failed Count (Red)

- Messages that couldn't be sent
- Reasons: Invalid number, network error, blocked
- Acceptable: <5% failure rate

### Remaining Count (Blue)

- Messages still in queue
- Updates as campaign progresses
- Helps estimate completion time

---

## 🔄 Resume Interrupted Campaigns

If you stop the bot or it crashes:

1. **CLI Mode Only**: Progress is saved automatically
2. **GUI Mode**: Currently doesn't support resume (planned feature)
3. **Workaround**:
   - Note the last successful message number from log
   - Remove processed rows from Excel
   - Re-import the remaining contacts

---

## 💡 Tips & Tricks

### Faster Setup

- Save your delay presets by noting slider positions
- Keep a template Excel file with correct column names
- Use the same file structure for all campaigns

### Better Results

- Personalize messages using the message column
- Include recipient name for better engagement
- Test different message formats to see what works

### Monitoring

- Keep log window visible during execution
- Take note of any patterns in failures
- Screenshot statistics for record-keeping

---

## 🆘 Getting Help

1. **Check Logs**: Review execution log for error details
2. **Read README**: Main documentation has troubleshooting section
3. **Test Minimal**: Try with just 2 contacts to isolate issue
4. **Check Settings**: Verify all configurations are correct

---

**GUI Version**: 1.0  
**Last Updated**: 2026-01-04  
**Compatible with**: WhatsApp Bot v1.0
