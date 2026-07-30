import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
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
def get_media_file(media_id: int, request: Request, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
        
    if media.source == "gdrive" or media.filepath.startswith("gdrive://"):
        file_id = media.filepath.replace("gdrive://", "")
        
        # Stream ALL media (including images) through the backend
        config_media = db.query(Media).filter(Media.source == "config", Media.filepath == "config://gdrive_token").first()
        if config_media and config_media.extra_meta:
            try:
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import AuthorizedSession
                
                creds = Credentials.from_authorized_user_info(config_media.extra_meta)
                authed_session = AuthorizedSession(creds)
                url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
                
                headers = {}
                if "range" in request.headers:
                    headers["Range"] = request.headers["range"]
                    
                response = authed_session.get(url, headers=headers, stream=True)
                
                # Forward necessary headers
                resp_headers = {}
                for h in ["Content-Range", "Accept-Ranges", "Content-Length"]:
                    if h in response.headers:
                        resp_headers[h] = response.headers[h]
                
                def generate():
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        yield chunk
                        
                return StreamingResponse(
                    generate(),
                    status_code=response.status_code,
                    headers=resp_headers,
                    media_type=media.mime_type
                )
            except Exception as e:
                print(f"Error streaming from Google Drive: {e}")
                
        # Fallback to redirect if streaming fails or token missing
        url = media.extra_meta.get('thumbnailLink') or media.extra_meta.get('webContentLink')
        if not url:
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
