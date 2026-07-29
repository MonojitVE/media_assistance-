from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import media, scan, command, demo, drive

# Creates the media table if it doesn't exist yet.
# For real migrations later, swap this for Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Media Assistant Backend")

from app.config import settings

frontend_url = settings.frontend_url.rstrip("/") if settings.frontend_url else ""

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url, 
        "http://localhost:3000", 
        "http://localhost:5173", 
        "https://media-assistance.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(media.router)
app.include_router(command.router)
app.include_router(demo.router)
app.include_router(drive.router)


@app.get("/")
def root():
    return {"status": "ok"}
