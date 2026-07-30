import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Media

def organize_files(db: Session, media_root: str) -> dict:
    """
    Moves local physical files into subfolders within media_root 
    based on their subtype (e.g., screenshots, whatsapp, photo).
    Updates their paths in the database.
    """
    root_path = Path(media_root)
    if not root_path.exists():
        raise FileNotFoundError(f"Media root does not exist: {root_path}")

    stats = {"moved": 0, "skipped": 0, "errored": 0}

    # Only process local files
    local_media = db.query(Media).filter(Media.source == "local").all()

    for item in local_media:
        current_path = Path(item.filepath)
        if not current_path.exists():
            stats["skipped"] += 1
            continue

        subtype = item.subtype or "other"
        # Determine target folder
        target_folder = root_path / subtype
        
        # Check if the file is already in its target folder
        if current_path.parent == target_folder:
            stats["skipped"] += 1
            continue
            
        target_folder.mkdir(parents=True, exist_ok=True)
        target_path = target_folder / current_path.name

        # If a file with the same name already exists in target but it's not the exact same file
        if target_path.exists():
            # append a timestamp or unique suffix to avoid overwriting
            target_path = target_folder / f"{current_path.stem}_{item.id}{current_path.suffix}"

        try:
            shutil.move(str(current_path), str(target_path))
            item.filepath = str(target_path.resolve())
            db.commit()
            stats["moved"] += 1
        except Exception as e:
            print(f"Error moving file {current_path}: {e}")
            db.rollback()
            stats["errored"] += 1

    return stats
