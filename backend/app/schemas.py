from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaOut(BaseModel):
    id: int
    filename: str
    filepath: str
    mime_type: str
    type: str
    subtype: str
    duration_sec: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanResult(BaseModel):
    added: int
    skipped: int
    errored: int
