from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from db.models import Vehicle
from db.session import get_db
from utils.helpers import save_upload_file, save_vehicle_to_db, format_vehicle_response


router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.post("/upload/")
async def upload_vehicle(
    number: str = Form(...),
    owner: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new vehicle with image."""
    file_location = await save_upload_file(image, image.filename)
    vehicle = await save_vehicle_to_db(db, number, owner, file_location)
    response = format_vehicle_response(vehicle)
    return response


@router.get("/")
async def get_vehicles(db: Session = Depends(get_db)):
    """Get all vehicles."""
    vehicles = db.query(Vehicle).all()
    return [format_vehicle_response(v) for v in vehicles]


@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Delete a vehicle by ID."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted"}
