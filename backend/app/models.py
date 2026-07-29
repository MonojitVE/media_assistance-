from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)

    # File identity
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False, unique=True, index=True)  # absolute path, dedup key
    mime_type = Column(String, nullable=False, index=True)

    # Classification — this is what your voice queries filter on
    type = Column(String, nullable=False, index=True)      # image | video | audio
    subtype = Column(String, nullable=False, index=True)    # photo | screenshot | short | long

    # Media-specific attributes
    duration_sec = Column(Float, nullable=True)   # video/audio only
    width = Column(Integer, nullable=True)         # image/video only
    height = Column(Integer, nullable=True)

    # Anything extra from EXIF / ffprobe / mutagen that doesn't need its own column
    extra_meta = Column(JSON, nullable=True)

    # Timestamps
    file_created_at = Column(DateTime, nullable=True)   # from filesystem/EXIF, when the media was actually made
    scanned_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("filepath", name="uq_media_filepath"),
    )
