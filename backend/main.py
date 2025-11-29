from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
def upload_vehicle(number: str = Form(...), owner: str = Form(...), image: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{image.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    db = SessionLocal()
    vehicle = Vehicle(number=number, owner=owner, image_path=file_location)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    db.close()
    return {"id": vehicle.id, "number": number, "owner": owner, "image_path": file_location}

@app.get("/vehicles/")
def get_vehicles():
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()
    return [{"id": v.id, "number": v.number, "owner": v.owner, "image_path": v.image_path} for v in vehicles]

@app.get("/image/{vehicle_id}")
def get_image(vehicle_id: int):
    db = SessionLocal()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    db.close()
    if vehicle:
        return FileResponse(vehicle.image_path)
    return {"error": "Image not found"}
