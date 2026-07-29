import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Media
from app.schemas import MediaOut

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[MediaOut])
def list_media(
    type: Optional[str] = None,       # image | video | audio
    subtype: Optional[str] = None,    # photo | screenshot | short | long
    folders: list[str] = Query(default=[]),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Media)
    if type:
        query = query.filter(Media.type == type)
    if subtype:
        query = query.filter(Media.subtype == subtype)
    if folders:
        query = query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))
    return query.limit(limit).all()


@router.get("/stats")
def media_stats(folders: list[str] = Query(default=[]), db: Session = Depends(get_db)):
    from sqlalchemy import func
    query = db.query(Media.type, Media.subtype, func.count(Media.id))
    
    if folders:
        query = query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))
        
    rows = query.group_by(Media.type, Media.subtype).all()
    return [{"type": t, "subtype": s, "count": c} for t, s, c in rows]


@router.get("/file/{media_id}")
def get_media_file(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
        
    if media.source == "gdrive" or media.filepath.startswith("gdrive://"):
        # Use thumbnailLink or webContentLink if we have them (bypasses cookie issues)
        url = media.extra_meta.get('thumbnailLink') or media.extra_meta.get('webContentLink')
        
        if not url:
            # Fallback to the generic Google Drive viewing URL
            file_id = media.filepath.replace("gdrive://", "")
            url = f"https://drive.google.com/uc?export=view&id={file_id}"
            
        return RedirectResponse(url)
        
    if not os.path.exists(media.filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(media.filepath)


@router.get("/folders")
def get_media_folders(db: Session = Depends(get_db)):
    # Retrieve all file paths and extract unique directory names
    paths = db.query(Media.filepath).distinct().all()
    folders = set()
    for (p,) in paths:
        folders.add(os.path.dirname(p))
    return sorted(list(folders))
