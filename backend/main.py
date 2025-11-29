from fastapi import HTTPException
# ...existing code...
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil, os

app = FastAPI()

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./vehicles.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    owner = Column(String, index=True)
    image_path = Column(String)
    timestamp = Column(String)

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Background keep-alive task: periodically ping the public URL
KEEP_ALIVE_URL = "https://vehiciq-2.onrender.com/"
KEEP_ALIVE_INTERVAL = 60  # seconds (10 minutes)

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


@app.on_event("startup")
async def _startup_keep_alive():
    # attach task to app state so it can be cancelled on shutdown
    app.state._keep_alive_task = asyncio.create_task(_keep_alive_loop())


@app.on_event("shutdown")
async def _shutdown_keep_alive():
    task = getattr(app.state, "_keep_alive_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

@app.get("/")
async def root():
    return {"message": "VehicIQ API is running!"}

@app.post("/upload/")
def upload_vehicle(number: str = Form(...), owner: str = Form(...), image: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{image.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    db = SessionLocal()
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vehicle = Vehicle(number=number, owner=owner, image_path=file_location, timestamp=timestamp)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    db.close()
    return {"id": vehicle.id, "number": number, "owner": owner, "image_path": file_location, "timestamp": timestamp}

@app.get("/vehicles/")
def get_vehicles():
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()
    return [{"id": v.id, "number": v.number, "owner": v.owner, "image_path": v.image_path, "timestamp": v.timestamp} for v in vehicles]

@app.get("/image/{vehicle_id}")
def get_image(vehicle_id: int):
    db = SessionLocal()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    db.close()
    if vehicle:
        return FileResponse(vehicle.image_path)
    return {"error": "Image not found"}

@app.delete("/vehicle/{vehicle_id}")
def delete_vehicle(vehicle_id: int):
    db = SessionLocal()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        db.close()
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    db.close()
    return {"message": "Vehicle deleted"}