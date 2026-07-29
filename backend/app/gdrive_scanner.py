import google.oauth2.credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import datetime

from app.database import engine, SessionLocal
from app.models import Media

class GDriveScanner:
    def __init__(self, credentials_dict):
        self.creds = google.oauth2.credentials.Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token')
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def scan_drive(self):
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}
        
        # We query for images, videos, and audio files
        query = "mimeType contains 'image/' or mimeType contains 'video/' or mimeType contains 'audio/'"
        
        try:
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, imageMediaMetadata, videoMediaMetadata, createdTime, size)",
                spaces='drive'
            ).execute()
            
            items = results.get('files', [])
            
            with SessionLocal() as db:
                for item in items:
                    try:
                        self.process_file(db, item, stats)
                    except Exception as e:
                        print(f"Error processing {item.get('name')}: {e}")
                        stats["errors"] += 1
                        
                db.commit()
                
            return stats
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e

    def process_file(self, db: Session, item: dict, stats: dict):
        file_id = item['id']
        filename = item['name']
        mime_type = item['mimeType']
        created_time_str = item.get('createdTime')
        
        created_time = None
        if created_time_str:
            created_time = datetime.datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
            
        filepath = f"gdrive://{file_id}"
        
        media_type = mime_type.split('/')[0]
        subtype = "unknown"
        duration = None
        width = None
        height = None
        extra_meta = {}
        
        if media_type == 'image':
            subtype = 'photo'
            metadata = item.get('imageMediaMetadata', {})
            width = metadata.get('width')
            height = metadata.get('height')
            if 'time' in metadata:
                extra_meta['exif_time'] = metadata['time']
                
        elif media_type == 'video':
            metadata = item.get('videoMediaMetadata', {})
            width = metadata.get('width')
            height = metadata.get('height')
            
            duration_ms = metadata.get('durationMillis')
            if duration_ms:
                duration = float(duration_ms) / 1000.0
                if duration > 120:
                    subtype = 'long'
                else:
                    subtype = 'short'
            else:
                subtype = 'video'
                
        elif media_type == 'audio':
            subtype = 'audio'
            
        stmt = insert(Media).values(
            source="gdrive",
            filename=filename,
            filepath=filepath,
            mime_type=mime_type,
            type=media_type,
            subtype=subtype,
            duration_sec=duration,
            width=width,
            height=height,
            extra_meta=extra_meta,
            file_created_at=created_time
        )
        
        update_dict = {
            c.name: c for c in stmt.excluded if not c.primary_key
        }
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['source', 'filepath'],
            set_=update_dict
        )
        
        db.execute(stmt)
        stats["added"] += 1
