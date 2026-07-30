import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import mimetypes
from PIL import Image
from mutagen import File as MutagenFile

from app.config import settings

SCREENSHOT_FILENAME_PATTERNS = [
    r"^screenshot",
    r"^screen[\s_-]?shot",
    r"^img_\d+\.png$",
]

COMMON_SCREEN_RESOLUTIONS = {
    (1920, 1080), (2560, 1440), (3840, 2160),
    (1170, 2532), (1080, 2340), (1284, 2778),  # common phone screen sizes
}


def real_mime_type(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def looks_like_screenshot_name(filename: str) -> bool:
    lower = filename.lower()
    return any(re.match(p, lower) for p in SCREENSHOT_FILENAME_PATTERNS)


WHATSAPP_FILENAME_PATTERNS = [
    r"^whatsapp image",
    r"^whatsapp video",
    r"^img-\d{8}-wa\d+",
    r"^vid-\d{8}-wa\d+",
]

def looks_like_whatsapp_name(filename: str) -> bool:
    lower = filename.lower()
    return any(re.match(p, lower) for p in WHATSAPP_FILENAME_PATTERNS)

def get_image_exif(path: str) -> dict:
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            return {}
        from PIL.ExifTags import TAGS
        return {TAGS.get(k, k): v for k, v in exif.items() if isinstance(k, int)}
    except Exception:
        return {}


def classify_image(path: str, filename: str) -> dict:
    img = Image.open(path)
    width, height = img.size
    exif = get_image_exif(path)

    # Strongest signal: real camera metadata
    has_camera_meta = bool(exif.get("Make") or exif.get("Model"))

    if looks_like_whatsapp_name(filename):
        subtype = "whatsapp"
    elif has_camera_meta:
        subtype = "photo"
    elif looks_like_screenshot_name(filename) or (width, height) in COMMON_SCREEN_RESOLUTIONS:
        subtype = "screenshot"
    else:
        subtype = "photo"  # default fallback; flagged for AI-vision review later if needed

    return {
        "type": "image",
        "subtype": subtype,
        "width": width,
        "height": height,
        "extra_meta": {"exif_make": exif.get("Make"), "exif_model": exif.get("Model")},
    }


def classify_video(path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    duration = float(data["format"].get("duration", 0))
    video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), {})

    p = Path(path)
    if looks_like_whatsapp_name(p.name):
        subtype = "whatsapp"
    else:
        subtype = "short" if duration < settings.short_media_threshold_sec else "long"

    return {
        "type": "video",
        "subtype": subtype,
        "duration_sec": duration,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "extra_meta": {"codec": video_stream.get("codec_name")},
    }


def classify_audio(path: str) -> dict:
    audio = MutagenFile(path)
    duration = audio.info.length if audio and audio.info else 0
    subtype = "short" if duration < settings.short_media_threshold_sec else "long"

    tags = {}
    if audio:
        tags = {
            "title": str(audio.get("TIT2", "")) if audio.get("TIT2") else None,
            "artist": str(audio.get("TPE1", "")) if audio.get("TPE1") else None,
        }

    return {
        "type": "audio",
        "subtype": subtype,
        "duration_sec": duration,
        "extra_meta": tags,
    }


def classify_file(path: str) -> Optional[dict]:
    """
    Runs the full cascade on a single file and returns a dict ready to
    be merged into a Media row, or None if the file type isn't supported.
    """
    p = Path(path)
    mime = real_mime_type(path)

    try:
        if mime.startswith("image/"):
            result = classify_image(path, p.name)
        elif mime.startswith("video/"):
            result = classify_video(path)
        elif mime.startswith("audio/"):
            result = classify_audio(path)
        else:
            return None
    except Exception as e:
        # Don't let one corrupt file kill the whole scan
        return {
            "type": "unknown",
            "subtype": "unclassified",
            "extra_meta": {"error": str(e)},
        }

    result["filename"] = p.name
    result["filepath"] = str(p.resolve())
    result["mime_type"] = mime
    result["file_created_at"] = datetime.fromtimestamp(p.stat().st_mtime)
    return result
