from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db
from .. import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Add validation logic later
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
    return db_project

@router.get("/", response_model=list[schemas.ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(models.TravelProject).all()
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.TravelProject).filter(models.TravelProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return db_project

