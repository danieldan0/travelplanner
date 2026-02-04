from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db
from .. import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if len(project.places) > 10:
        raise HTTPException(status_code=400, detail="Cannot add more than 10 places to a project")
    if len(set(p.external_id for p in project.places)) != len(project.places):
        raise HTTPException(status_code=400, detail="Duplicate external_id values in places")
    db_project = models.TravelProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        places=[
            models.Place(
                external_id=place.external_id,
                notes=place.notes
            ) for place in project.places
        ]
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return project_to_out(db_project)

@router.get("/", response_model=list[schemas.ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(models.TravelProject).all()
    return [project_to_out(project) for project in projects]

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project_to_out(db_project)

@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    if project.start_date is not None:
        db_project.start_date = project.start_date

    if project.places is not None:
        if len(project.places) > 10:
            raise HTTPException(status_code=400, detail="Cannot add more than 10 places to a project")
        if len(set(p.external_id for p in project.places)) != len(project.places):
            raise HTTPException(status_code=400, detail="Duplicate external_id values in places")
        existing = {p.id: p for p in db_project.places}
        seen_ids: set[int] = set()

        for place in project.places:
            if place.id is not None and place.id in existing:
                db_place = existing[place.id]
                if place.external_id is not None and place.external_id != db_place.external_id:
                    raise HTTPException(status_code=400, detail="external_id cannot be updated")
                if place.notes is not None:
                    db_place.notes = place.notes
                if place.visited is not None:
                    db_place.visited = place.visited
                seen_ids.add(place.id)
            else:
                db.add(models.Place(
                    external_id = place.external_id,
                    notes = place.notes,
                    visited = place.visited or False,
                    project_id = project_id
                ))

        for place_id, db_place in existing.items():
            if place_id not in seen_ids:
                db.delete(db_place)


    db.commit()
    db.refresh(db_project)
    return project_to_out(db_project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    visited_place = db.query(models.Place).filter(
        models.Place.project_id == project_id,
        models.Place.visited == True
    ).first()
    if visited_place:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete project with visited places")
    db.delete(db_project)
    db.commit()
    return

def project_to_out(project: models.TravelProject) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id = project.id,
        name = project.name,
        description = project.description,
        start_date = project.start_date,
        places = [
            schemas.PlaceOut(
                id = place.id,
                name = place.name,
                external_id = place.external_id,
                notes = place.notes,
                visited = place.visited
            ) for place in project.places
        ],
        completed = all(place.visited for place in project.places)
    )