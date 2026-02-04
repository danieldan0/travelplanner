from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..services.art_api import validate_artwork

from ..dependencies import get_db
from .. import models, schemas

router = APIRouter()

@router.post("/{project_id}/places", response_model=schemas.PlaceOut, status_code=status.HTTP_201_CREATED)
def create_place(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)
):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    existing_place = db.query(models.Place).filter(
        models.Place.project_id == project_id,
        models.Place.external_id == place.external_id
    ).first()
    if existing_place:
        raise HTTPException(status_code=400, detail="Place with this external_id already exists in the project")
    place_count = db.query(models.Place).filter(models.Place.project_id == project_id).count()
    if place_count >= 10:
        raise HTTPException(status_code=400, detail="Cannot add more than 10 places to a project")
    data = validate_artwork(place.external_id)
    db_place = models.Place(
        external_id = place.external_id,
        name = data.get("title"),
        notes = place.notes,
        project_id = project_id
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

@router.put("/{project_id}/places/{place_id}", response_model=schemas.PlaceOut)
def update_place(project_id: int, place_id: int, place: schemas.PlaceUpdate, db: Session = Depends(get_db)
):
    db_place = db.query(models.Place).filter(
        models.Place.id == place_id,
        models.Place.project_id == project_id
    ).first()
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    if place.external_id is not None and place.external_id != db_place.external_id:
        raise HTTPException(status_code=400, detail="external_id cannot be updated")
    if place.notes is not None:
        db_place.notes = place.notes
    if place.visited is not None:
        db_place.visited = place.visited

    db.commit()
    db.refresh(db_place)
    return db_place