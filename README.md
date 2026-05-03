# 🎧 PDF AudioBook — Kivy Android App

Convert any PDF into an MP3 AudioBook, with full AdMob monetization.

---

## 📁 Project Structure

```
pdf_audiobook/
├── main.py                  # App entry point
├── buildozer.spec           # Android build config
├── ads/
│   ├── __init__.py
│   └── admob_manager.py     # Banner + Interstitial ad logic
├── core/
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF → text (PyMuPDF / pypdf)
│   ├── tts_engine.py        # Text → MP3 (gTTS / pyttsx3)
│   └── file_picker.py       # Native Android file picker
└── ui/
    ├── __init__.py
    ├── screens.py           # SplashScreen, HomeScreen, GenerateScreen
    └── widgets.py           # RoundedButton, CardBox, BannerAdWidget, etc.
```

---

## 🚀 Quick Setup

### 1. Install Python Dependencies (development/testing)

```bash
pip install kivy==2.3.0 pymupdf pypdf gtts pyttsx3 pydub requests
```

### 2. Run on Desktop (for UI testing)

```bash
cd pdf_audiobook
python main.py
```

> AdMob ads won't show on desktop — they're replaced by placeholders. Everything else works.

---

## 📱 Build for Android

### Requirements

- Ubuntu / macOS (WSL2 on Windows also works)
- Python 3.10+
- Java JDK 17
- Android SDK + NDK (Buildozer installs these automatically)

### Install Buildozer

```bash
pip install buildozer cython
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-dev \
    libffi-dev libssl-dev libjpeg-dev zlib1g-dev build-essential
```

### Build APK

```bash
cd pdf_audiobook
buildozer android debug         # debug APK (~10-15 min first time)
buildozer android release       # release APK (for Play Store)
```

The APK is output to: `bin/pdfaudiobook-1.0.0-arm64-v8a-debug.apk`

### Deploy to Device

```bash
buildozer android deploy run    # builds + installs + runs on connected device
```

---

## 💰 AdMob Monetization Setup

### Step 1: Create AdMob Account
1. Go to https://admob.google.com
2. Sign in with your Google account
3. Add a new app (Android)

### Step 2: Get Your Ad Unit IDs
Create 2 ad units in the AdMob dashboard:
- **Banner Ad** (320×50 or Adaptive)
- **Interstitial Ad** (full-screen)

### Step 3: Replace Test IDs in Code

Edit `ads/admob_manager.py`:

```python
# Replace these with YOUR real ad unit IDs:
ADMOB_APP_ID         = "ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX"
BANNER_AD_UNIT_ID    = "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX"
INTERSTITIAL_AD_UNIT = "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX"
```

Edit `buildozer.spec`:

```ini
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX
```

> ⚠️ NEVER ship the app with test Ad Unit IDs — your account will be suspended.

### Ad Placement Summary

| Trigger | Ad Type | Location in Code |
|---------|---------|-----------------|
| App opens | Interstitial (video) | `main.py → on_start()` |
| Tap "Generate AudioBook" | Interstitial (video) | `screens.py → _on_generate()` |
| Tap "Download / Save MP3" | Interstitial (video) | `screens.py → _on_download()` |
| Always visible | Banner (bottom) | `HomeScreen` + `GenerateScreen` |

---

## 🎙 TTS Engine Details

The app uses **gTTS (Google Text-to-Speech)** as primary engine:
- Requires internet connection
- Natural sounding voices
- Supports 10+ languages (see `tts_engine.py → SUPPORTED_LANGUAGES`)
- Large PDFs are split into 4000-char chunks and merged

Fallback: **pyttsx3** (offline, robotic voice, no internet needed)

---

## 📄 PDF Support

- ✅ Text-based PDFs (most books, reports, papers)
- ❌ Scanned/image PDFs (no OCR — add pytesseract for that)
- ✅ Multi-page PDFs (chunked processing with progress bar)

---

## 🔧 Common Issues

### "No module named 'fitz'"
```bash
pip install pymupdf
```

### "No module named 'gtts'"
```bash
pip install gTTS
```

### Build fails on `libffi`
```bash
sudo apt-get install libffi-dev
```

### AdMob test ads not showing
- Make sure your device has Google Play Services
- Allow 1-2 minutes for first ad load after app init
- Check logcat: `adb logcat | grep -i admob`

---

## 📝 Publishing Checklist

- [ ] Replace all test Ad Unit IDs with real ones
- [ ] Update `buildozer.spec`: `package.domain`, `version`
- [ ] Add app icon: `assets/icon.png` (512×512)
- [ ] Add splash: `assets/splash.png` (1024×500)
- [ ] Build release APK: `buildozer android release`
- [ ] Sign APK with your keystore
- [ ] Test on real Android device (API 24+)
- [ ] Submit to Google Play Console

---

## 📜 License

MIT — free to use and modify.
