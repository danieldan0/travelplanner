from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db
from .. import models, schemas

router = APIRouter()

@router.post("/{project_id}/places", response_model=schemas.PlaceOut, status_code=status.HTTP_201_CREATED)
def create_place(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)
):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Add external id validation later
    db_place = models.Place(
        external_id=place.external_id, 
        notes=place.notes, 
        project_id=project_id
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.get("/{project_id}/places", response_model=list[schemas.PlaceOut])
def get_places(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    places = db.query(models.Place).filter(models.Place.project_id == project_id).all()
    return places

@router.get("/{project_id}/places/{place_id}", response_model=schemas.PlaceOut)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    db_place = db.query(models.Place).filter(
        models.Place.id == place_id,
        models.Place.project_id == project_id
    ).first()
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place