from datetime import date
from sqlalchemy import Integer, String, ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

class TravelProject(Base):
    __tablename__ = "travel_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    places: Mapped[list["Place"]] = relationship(
        "Place",
        back_populates="project",
        cascade="all, delete-orphan",
    )

class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    external_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    visited: Mapped[bool] = mapped_column(Boolean, default=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("travel_projects.id"))

    project: Mapped["TravelProject"] = relationship("TravelProject", back_populates="places")

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_place"),
    )