from pathlib import Path

from sqlalchemy.orm import Session

from app.classifier import classify_file
from app.config import settings
from app.models import Media

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic",
    ".mp4", ".mov", ".mkv", ".avi", ".webm",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg",
}


def scan_directory(db: Session, root: str | None = None) -> dict:
    """
    Walks the media root, classifies every new/changed file, and
    upserts it into the media table. Returns a summary of what happened.
    """
    root_path = Path(root or settings.media_root)
    if not root_path.exists():
        raise FileNotFoundError(f"Media root does not exist: {root_path}")

    added, skipped, errored = 0, 0, 0

    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        abs_path = str(file_path.resolve())

        # Skip files already indexed (dedup on filepath)
        existing = db.query(Media).filter(Media.filepath == abs_path).first()
        if existing:
            skipped += 1
            continue

        result = classify_file(abs_path)
        if result is None:
            skipped += 1
            continue

        try:
            media = Media(**result)
            db.add(media)
            db.commit()
            added += 1
        except Exception:
            db.rollback()
            errored += 1

    return {"added": added, "skipped": skipped, "errored": errored}
