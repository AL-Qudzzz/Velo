# WhatsApp Bot GUI - Enhanced Features Guide

## 🆕 New Features

### 1. ⏱️ Countdown Timer

**Real-time countdown display** untuk delay antar pesan

**Fitur:**

- Tampilan besar dengan format **MM:SS** (misal: 03:00 untuk 3 menit)
- Update setiap detik
- Menampilkan info kontak berikutnya
- Warna kuning untuk visibility

**Lokasi:** Tab "▶️ Execution" - di atas progress bar

---

### 2. ⏸️ Pause & Resume

**Save progress dan lanjutkan kapan saja**

**Cara Kerja:**

1. Klik **⏸️ Pause** saat bot sedang jalan
2. Progress otomatis tersimpan ke `progress_gui.json`
3. Bot berhenti, browser tetap terbuka
4. Klik **▶️ Resume** untuk melanjutkan
5. Atau tutup aplikasi, jalankan lagi nanti - akan ditanya "Resume?"

**Data yang Disimpan:**

- Posisi terakhir (message ke berapa)
- Daftar kontak
- Success/failed count
- Failed numbers list
- Timestamp

**Auto-Resume:**

- Saat buka aplikasi, jika ada progress tersimpan → muncul dialog
- Pilih "Yes" untuk lanjutkan, "No" untuk mulai baru

---

### 3. 🔒 Fixed Delay Mode

**Delay tetap tanpa randomisasi**

**Cara Aktifkan:**

1. Tab "⏱️ Delay Settings"
2. Centang **"🔒 Use Fixed Delay (no randomization)"**
3. Slider jitter otomatis disabled
4. Delay akan **selalu sama persis**

**Contoh:**

- Set Base Delay = 180 detik (3 menit)
- Enable Fixed Delay
- **Setiap pesan akan delay TEPAT 3 menit**, tidak kurang tidak lebih

**Preset Cepat:**

- Klik **"⏱️ Fixed 3min"** untuk langsung set 3 menit fixed

**Kegunaan:**

- Untuk campaign yang butuh timing konsisten
- Lebih mudah prediksi waktu selesai
- Cocok untuk testing

---

### 4. 📄 Failed Numbers Log

**Track dan export nomor yang gagal**

**Fitur:**

- Semua nomor gagal otomatis tercatat
- Menyimpan: phone, name, reason, timestamp
- Bisa di-export ke file TXT/CSV

**Cara Export:**

1. Tab "▶️ Execution"
2. Klik **"📄 Export Failed Numbers"** (di bawah statistics)
3. Pilih lokasi save
4. File berisi daftar lengkap nomor yang gagal

**Format File:**

```
Failed WhatsApp Numbers
============================================================
Generated: 2026-01-12 22:00:00
Total Failed: 5
============================================================

1. John Doe
   Phone: 628123456789
   Reason: Send failed
   Time: 2026-01-12T22:00:00

2. Jane Smith
   Phone: 628234567890
   Reason: Invalid number
   Time: 2026-01-12T22:05:00
...
```

---

## 🎯 Workflow Lengkap

### Scenario 1: Campaign Baru dengan Fixed Delay

1. **Setup File** (Tab 1)

   - Load Excel
   - Auto-detect columns

2. **Set Delay** (Tab 2)

   - Centang "🔒 Use Fixed Delay"
   - Set Base Delay = 180s (3 menit)
   - Atau klik preset "⏱️ Fixed 3min"

3. **Execute** (Tab 3)
   - Klik "▶️ Start Sending"
   - Lihat countdown: 03:00 → 02:59 → 02:58 ...
   - Setiap pesan delay **tepat 3 menit**

---

### Scenario 2: Pause dan Resume

1. **Start Campaign**

   - Mulai kirim pesan
   - Sudah kirim 20 dari 100 pesan

2. **Pause**

   - Klik "⏸️ Pause"
   - Progress tersimpan otomatis
   - Tutup aplikasi jika perlu

3. **Resume (Hari Berikutnya)**
   - Buka aplikasi lagi
   - Muncul dialog: "Resume from message 21?"
   - Klik "Yes"
   - Lanjut dari message 21 tanpa setup ulang

---

### Scenario 3: Export Failed Numbers

1. **Setelah Campaign Selesai**

   - Lihat statistics: Failed = 8

2. **Export**

   - Klik "📄 Export Failed Numbers"
   - Save as `failed_20260112.txt`

3. **Review**
   - Buka file
   - Lihat daftar 8 nomor yang gagal
   - Bisa di-follow up manual atau perbaiki data

---

## 📊 UI Changes

### Tab 1: File & Columns

- ✅ Sama seperti sebelumnya

### Tab 2: Delay Settings

- ✅ **NEW:** Checkbox "🔒 Use Fixed Delay"
- ✅ **NEW:** Preset button "⏱️ Fixed 3min"
- ✅ Jitter sliders disabled saat fixed mode

### Tab 3: Execution

- ✅ **NEW:** Countdown timer display (besar, kuning)
- ✅ **NEW:** Next message info
- ✅ **NEW:** Pause button (terpisah dari Stop)
- ✅ **NEW:** Export failed numbers button
- ✅ Improved statistics display

---

## 🔧 Technical Details

### Progress File Location

```
d:\Coding\AutoBlast\progress_gui.json
```

### Progress File Structure

```json
{
  "file_name": "contacts.xlsx",
  "contacts": [...],
  "current_index": 25,
  "success_count": 23,
  "failed_count": 2,
  "failed_contacts": [...],
  "timestamp": "2026-01-12T22:00:00"
}
```

### Countdown Update Frequency

- Updates every **1 second**
- Thread-safe UI updates
- Pauses when bot is paused

### Fixed Delay Calculation

```python
if use_fixed_delay:
    delay = base_delay  # Exact value
else:
    delay = base_delay + warmup + jitter  # Variable
```

---

## ⚠️ Important Notes

### Pause vs Stop

- **Pause:** Simpan progress, browser tetap buka, bisa resume
- **Stop:** Simpan progress, tutup browser, harus setup ulang driver

### Fixed Delay Recommendations

- **3 minutes (180s):** Sangat aman, cocok untuk campaign besar
- **2 minutes (120s):** Aman, balanced
- **1 minute (60s):** Minimum recommended

### Failed Numbers

- Tersimpan di memory selama session
- Export sebelum close aplikasi
- Auto-saved di progress file jika pause/stop

---

## 🎉 Benefits

### Countdown Timer

✅ Tahu persis berapa lama lagi
✅ Tidak perlu tebak-tebak
✅ Bisa monitor dari jauh

### Pause/Resume

✅ Fleksibilitas tinggi
✅ Tidak perlu selesai dalam 1 session
✅ Aman dari interrupt

### Fixed Delay

✅ Timing konsisten
✅ Mudah prediksi
✅ Cocok untuk testing

### Failed Numbers Log

✅ Track semua kegagalan
✅ Bisa follow-up manual
✅ Analisa pola kegagalan

---

**Version:** 2.0 Enhanced  
**Date:** 2026-01-12  
**New Features:** 4 major enhancements
