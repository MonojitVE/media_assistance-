from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Media
from app.schemas import MediaOut

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[MediaOut])
def list_media(
    type: Optional[str] = None,       # image | video | audio
    subtype: Optional[str] = None,    # photo | screenshot | short | long
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Media)
    if type:
        query = query.filter(Media.type == type)
    if subtype:
        query = query.filter(Media.subtype == subtype)
    return query.limit(limit).all()


@router.get("/stats")
def media_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = (
        db.query(Media.type, Media.subtype, func.count(Media.id))
        .group_by(Media.type, Media.subtype)
        .all()
    )
    return [{"type": t, "subtype": s, "count": c} for t, s, c in rows]
