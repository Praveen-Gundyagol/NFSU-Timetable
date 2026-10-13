from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_TITLE, APP_VERSION
from app.database import engine, Base
import app.models # registers all models
from app.routers import config, resources, academic, timetable

# Auto-create SQLite database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Automated Timetable Generation Backend using Google OR-Tools CP-SAT and SQLite."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(config.router)
app.include_router(resources.router)
app.include_router(academic.router)
app.include_router(timetable.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "solver": "Google OR-Tools CP-SAT Ready"
    }
