from fastapi import FastAPI
from .db import engine
from .models import Base
from contextlib import asynccontextmanager
from .routers import projects, places

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    pass

app = FastAPI(lifespan = lifespan, title="Travel Planner API", version="1.0.0")
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(places.router, prefix="/projects", tags=["places"])
