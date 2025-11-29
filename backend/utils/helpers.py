import asyncio
import os
import shutil
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Vehicle
import httpx
from PIL import Image
import io
from pathlib import Path

# Background keep-alive task: periodically ping the public URL
KEEP_ALIVE_URL = "https://vehiciq-2.onrender.com/"
KEEP_ALIVE_INTERVAL = 60  # seconds (10 minutes)

UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_IMAGE_WIDTH = 1024
MAX_IMAGE_HEIGHT = 768
IMAGE_QUALITY = 85


async def save_upload_file(file, filename: str) -> str:
    """Save and optimize uploaded image to disk and return the file location."""
    # Read file into memory
    content = await file.read()
    
    # Optimize image
    try:
        img = Image.open(io.BytesIO(content))
        
        # Resize if needed
        img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        
        # Save optimized image
        file_location = f"{UPLOAD_DIR}/{Path(filename).stem}_opt.jpg"
        img.save(file_location, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
        return file_location
    except Exception as e:
        # Fallback: save original if optimization fails
        print(f"Image optimization failed: {e}, saving original")
        file_location = f"{UPLOAD_DIR}/{filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(content)
        return file_location


def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


async def save_vehicle_to_db(db: Session, number: str, owner: str, image_path: str) -> Vehicle:
    """Save vehicle record to database."""
    timestamp = get_current_timestamp()
    vehicle = Vehicle(number=number, owner=owner, image_path=image_path, timestamp=timestamp)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def format_vehicle_response(vehicle: Vehicle) -> dict:
    """Format vehicle object as response dictionary."""
    return {
        "id": vehicle.id,
        "number": vehicle.number,
        "owner": vehicle.owner,
        "image_path": vehicle.image_path,
        "timestamp": vehicle.timestamp
    }



async def _keep_alive_loop():
    # slight startup delay
    await asyncio.sleep(5)
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                resp = await client.get(KEEP_ALIVE_URL)
                # optional: log status
                print(f"Keep-alive ping status: {resp.status_code}")
            except Exception as e:
                print(f"Keep-alive ping failed: {e}")
            try:
                await asyncio.sleep(KEEP_ALIVE_INTERVAL)
            except asyncio.CancelledError:
                break