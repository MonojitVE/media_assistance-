from app.database import SessionLocal
from app.models import Media
from app.classifier import classify_file

def debug_classify():
    db = SessionLocal()
    media_items = db.query(Media).filter(Media.source == "local").all()
    print(f"Total local media items: {len(media_items)}")
    for item in media_items:
        result = classify_file(item.filepath)
        if result:
            print(f"File: {item.filename} | Original subtype: {item.subtype} | New subtype: {result.get('subtype')}")
        else:
            print(f"File: {item.filename} | Failed to classify.")
    db.close()

if __name__ == "__main__":
    debug_classify()
