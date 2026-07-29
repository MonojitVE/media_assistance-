from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.intent_parser import parse_command
from app.query_engine import get_ordered_media, get_mixed_playlist, get_slideshow
from app.schemas import MediaOut

router = APIRouter(prefix="/command", tags=["command"])


class CommandIn(BaseModel):
    text: str  # e.g. "show me mix videos", "play short audio", "show screenshots"
    folders: list[str] | None = None


class CommandOut(BaseModel):
    intent: dict
    playlist: list[MediaOut]


@router.post("", response_model=CommandOut)
def run_command(payload: CommandIn, db: Session = Depends(get_db)):
    intent = parse_command(payload.text)

    if intent["action"] == "slideshow":
        results = get_slideshow(db, subtype=intent["subtype"], folders=payload.folders)

    elif intent["action"] == "play" and intent.get("mode") == "mixed":
        results = get_mixed_playlist(db, type=intent["type"], folders=payload.folders)

    elif intent["action"] == "play" and intent.get("mode") == "ordered":
        results = get_ordered_media(
            db, type=intent["type"], subtype=intent.get("subtype"), order=intent.get("order", "shortest_first"), folders=payload.folders
        )

    else:
        results = []

    return {"intent": intent, "playlist": results}
