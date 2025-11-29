from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db.models import Vehicle
from db.session import get_db


router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/{vehicle_id}")
async def get_image(vehicle_id: int, db: Session = Depends(get_db)):
    """Get image for a specific vehicle."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        vehicle.image_path,
        headers={"Cache-Control": "public, max-age=3600"}
    )
