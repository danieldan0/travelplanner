from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class TravelProject(Base):
    __tablename__ = "travel_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True, nullable=True)
    start_date = Column(Date, nullable=True)

    places = relationship("Place", back_populates="project", cascade="all, delete-orphan")

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    external_id = Column(Integer, index=True, nullable=False)
    notes = Column(String, index=True, nullable=True)
    visited = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("travel_projects.id"))

    project = relationship("TravelProject", back_populates="places")

    __table_args__ = (
        UniqueConstraint('project_id', 'external_id', name='uq_project_place'),
    )