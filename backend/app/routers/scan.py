from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.scanner import scan_directory
from app.organizer import organize_files
from app.schemas import ScanResult
from app.config import settings

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", response_model=ScanResult)
def trigger_scan(root: str | None = None, db: Session = Depends(get_db)):
    try:
        result = scan_directory(db, root)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

@router.post("/organize")
def trigger_organize(root: str | None = None, db: Session = Depends(get_db)):
    try:
        media_root = root or settings.media_root
        result = organize_files(db, media_root)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
