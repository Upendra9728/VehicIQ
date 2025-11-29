# APK Build Guide for VehicIQ

## Prerequisites

You need Android SDK to build APKs. Here are FREE options:

### Option 1: Install Android Studio (Easy, ~2GB)
1. Download Android Studio: https://developer.android.com/studio
2. Install it
3. Run Android Studio and it will automatically install Android SDK
4. Configure Flutter:
   ```powershell
   flutter config --android-sdk "C:\Users\kalle\AppData\Local\Android\Sdk"
   ```

### Option 2: Install Command-Line Tools Only (Smaller, ~500MB)
1. Download Command Line Tools: https://developer.android.com/studio#downloads
   - Scroll down to "Command line tools only"
2. Extract to a folder, e.g., `C:\Android`
3. Install required SDK components:
   ```powershell
   cd C:\Android\cmdline-tools\bin
   .\sdkmanager --install "platforms;android-34" "build-tools;34.0.0"
   ```
4. Configure Flutter:
   ```powershell
   flutter config --android-sdk "C:\Android"
   ```

### Option 3: Using Existing Android Emulator/Device
If you have Android emulator or a physical device already set up, you can:
1. Connect device via USB (enable Developer Mode)
2. Run: `flutter run`
3. Flutter will handle everything

---

## Build APK (After SDK Setup)

Once Android SDK is installed:

```powershell
cd C:\Users\kalle\Documents\sairam\frontend

# Build debug APK (faster)
flutter build apk --debug

# Build release APK (optimized, for production)
flutter build apk --release
```

APK will be generated at:
- `build/app/outputs/flutter-apk/app-debug.apk` (debug)
- `build/app/outputs/flutter-apk/app-release.apk` (release)

---

## Install APK on Mobile

### Via USB (Requires ADB)
```powershell
# Connect your Android phone via USB
flutter install

# Or manually:
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Via File Transfer
1. Transfer APK to your phone
2. Open Files on your phone
3. Tap the APK and install

---

## Backend Setup on Mobile

For the app to work on your mobile:

1. **Backend must be running and accessible**
   - If backend is on the same network: Update `lib/main.dart`
   - Replace `http://localhost:8000` with your computer's IP (e.g., `http://192.168.x.x:8000`)
   - Or use ngrok for tunneling (free): https://ngrok.com/

2. **Run backend server**
   ```powershell
   cd C:\Users\kalle\Documents\sairam\backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Important:** Update the URL in Flutter app before building APK:
   - Edit `lib/main.dart`
   - Replace `localhost:8000` with your backend URL (e.g., `192.168.1.5:8000`)

---

## Troubleshooting

**APK not installing:**
- Check device Android version is 21+
- Enable "Install from Unknown Sources" in phone settings

**App can't connect to backend:**
- Ensure backend is running
- Check firewall allows traffic on port 8000
- Use same network (WiFi) for phone and computer
- Or use ngrok for remote access

---

## Quick Summary

1. Install Android SDK (Option 1 or 2 above)
2. Configure Flutter: `flutter config --android-sdk "path/to/sdk"`
3. Update backend URL in `lib/main.dart`
4. Build APK: `flutter build apk --release`
5. Transfer to phone and install

Need help with any step? Ask!
