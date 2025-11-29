# VehicIQ Backend (FastAPI)

This backend provides REST API endpoints for vehicle data storage and retrieval.

## Features
- Upload vehicle image (camera/gallery)
- Store vehicle details (number, etc.)
- Retrieve vehicle details and images
- Uses SQLite for storage

## Setup Instructions

1. Install Python 3.8+
2. Install dependencies:
   ```powershell
   pip install fastapi uvicorn sqlalchemy pillow python-multipart
   ```
3. Run the backend server:
   ```powershell
   uvicorn main:app --reload
   ```

API will be available at http://localhost:8000

---

# VehicIQ Frontend (Flutter)

This is a Flutter app for Android. It allows users to:
- Take/upload vehicle photo
- Enter vehicle details
- Upload to backend
- View stored vehicles

## Setup Instructions

1. Install Flutter SDK: https://docs.flutter.dev/get-started/install
2. Open the `frontend` folder in VS Code or Android Studio
3. Run the app:
   ```powershell
   flutter run
   ```
4. Build APK:
   ```powershell
   flutter build apk --release
   ```

---

# Project Structure
- `backend/` - FastAPI backend
- `frontend/` - Flutter app

---

For any issues, ask here for help!