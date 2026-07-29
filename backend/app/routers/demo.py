import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Media

router = APIRouter(prefix="/demo", tags=["demo"])


def _fake_row(i: int, type: str, subtype: str, duration_sec: float | None) -> dict:
    base_time = datetime.now() - timedelta(days=random.randint(0, 90))
    ext = {"video": "mp4", "audio": "mp3", "image": "jpg" if subtype == "photo" else "png"}[type]
    return {
        "filename": f"{subtype}_{i}.{ext}",
        "filepath": f"/demo/{type}/{subtype}_{i}.{ext}",  # fake path, demo-only
        "mime_type": f"{type}/{ext}",
        "type": type,
        "subtype": subtype,
        "duration_sec": duration_sec,
        "width": 1920 if type != "audio" else None,
        "height": 1080 if type != "audio" else None,
        "extra_meta": {"demo": True},
        "file_created_at": base_time,
    }


@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    rows = []

    for i in range(12):
        rows.append(_fake_row(i, "video", "short", round(random.uniform(10, 90), 1)))
    for i in range(4):
        rows.append(_fake_row(i, "video", "long", round(random.uniform(300, 1800), 1)))

    for i in range(8):
        rows.append(_fake_row(i, "audio", "short", round(random.uniform(15, 100), 1)))
    for i in range(3):
        rows.append(_fake_row(i, "audio", "long", round(random.uniform(200, 3600), 1)))

    for i in range(15):
        rows.append(_fake_row(i, "image", "photo", None))
    for i in range(10):
        rows.append(_fake_row(i, "image", "screenshot", None))

    inserted = 0
    for row in rows:
        exists = db.query(Media).filter(Media.filepath == row["filepath"]).first()
        if exists:
            continue
        db.add(Media(**row))
        inserted += 1

    db.commit()
    return {"inserted": inserted, "total_rows_prepared": len(rows)}


@router.delete("/clear")
def clear_demo_data(db: Session = Depends(get_db)):
    deleted = db.query(Media).filter(Media.filepath.like("/demo/%")).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}
