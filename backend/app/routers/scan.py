from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.scanner import scan_directory
from app.schemas import ScanResult

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", response_model=ScanResult)
def trigger_scan(root: str | None = None, db: Session = Depends(get_db)):
    try:
        result = scan_directory(db, root)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
