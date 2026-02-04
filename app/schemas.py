from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class PlaceCreate(BaseModel):
    external_id: int
    notes: Optional[str] = None

class PlaceUpdate(BaseModel):
    id: Optional[int] = None
    notes: Optional[str] = None
    visited: Optional[bool] = None
    external_id: Optional[int] = None

class PlaceOut(BaseModel):
    id: int
    name: Optional[str]
    external_id: int
    notes: Optional[str]
    visited: bool

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: List[PlaceCreate] = Field(default_factory=list, max_length=10)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: Optional[List[PlaceUpdate]] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    places: List[PlaceOut]

    class Config:
        from_attributes = True