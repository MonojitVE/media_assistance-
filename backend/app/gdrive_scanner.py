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
                fields="nextPageToken, files(id, name, mimeType, imageMediaMetadata, videoMediaMetadata, createdTime, size, thumbnailLink, webContentLink)",
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
                        
            return stats
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e

    def process_file(self, db: Session, item: dict, stats: dict):
        file_id = item['id']
        filename = item['name']
        mime_type = item['mimeType']
        created_time_str = item.get('createdTime')
        
        filepath = f"gdrive://{file_id}"
        
        # Skip files already indexed (dedup on source + filepath)
        existing = db.query(Media).filter(Media.source == "gdrive", Media.filepath == filepath).first()
        if existing:
            stats["skipped"] += 1
            return
            
        created_time = None
        if created_time_str:
            created_time = datetime.datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
        
        media_type = mime_type.split('/')[0]
        subtype = "unknown"
        duration = None
        width = None
        height = None
        extra_meta = {}
        
        if 'thumbnailLink' in item:
            # Get a larger thumbnail by replacing the default =s220 with =s1000
            extra_meta['thumbnailLink'] = item['thumbnailLink'].replace('=s220', '=s1000')
        if 'webContentLink' in item:
            extra_meta['webContentLink'] = item['webContentLink']
        
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
            
        try:
            media = Media(
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
            db.add(media)
            db.commit()
            stats["added"] += 1
        except Exception as e:
            print(f"Database error for {filename}: {e}")
            db.rollback()
            stats["errors"] += 1
