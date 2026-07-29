from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Media


def get_ordered_media(db: Session, type: str, subtype: str | None = None, order: str = "shortest_first", limit: int = 50, folders: list[str] | None = None):
    """
    Returns media of a given type, ordered by duration.
    order: 'shortest_first' or 'longest_first' (ignored for images).
    """
    query = db.query(Media).filter(Media.type == type)
    if subtype:
        query = query.filter(Media.subtype == subtype)
    if folders:
        query = query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))

    if type in ("video", "audio"):
        query = query.order_by(
            Media.duration_sec.asc() if order == "shortest_first" else Media.duration_sec.desc()
        )
    else:
        query = query.order_by(Media.file_created_at.asc())

    return query.limit(limit).all()


def get_mixed_playlist(db: Session, type: str, short_count: int = 3, long_count: int = 1, cycles: int = 5, folders: list[str] | None = None):
    """
    Builds a playlist alternating `short_count` short items then
    `long_count` long items, repeated for `cycles` rounds — this is
    the '3 short videos then 1 long video' pattern.
    Pulls shortest-first within each subtype so early items in each
    block are the quickest to load.
    """
    shorts_query = db.query(Media).filter(Media.type == type, Media.subtype == "short")
    longs_query = db.query(Media).filter(Media.type == type, Media.subtype == "long")

    if folders:
        shorts_query = shorts_query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))
        longs_query = longs_query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))

    shorts = (
        shorts_query
        .order_by(Media.duration_sec.asc())
        .limit(short_count * cycles)
        .all()
    )
    longs = (
        longs_query
        .order_by(Media.duration_sec.asc())
        .limit(long_count * cycles)
        .all()
    )

    playlist = []
    si, li = 0, 0
    for _ in range(cycles):
        block_shorts = shorts[si: si + short_count]
        block_longs = longs[li: li + long_count]
        if not block_shorts and not block_longs:
            break
        playlist.extend(block_shorts)
        playlist.extend(block_longs)
        si += short_count
        li += long_count

    return playlist


def get_slideshow(db: Session, subtype: str = "screenshot", limit: int = 100, folders: list[str] | None = None):
    """Screenshots (or photos) in chronological order for slideshow playback."""
    query = db.query(Media).filter(Media.type == "image", Media.subtype == subtype)
    if folders:
        query = query.filter(or_(*[Media.filepath.startswith(f.replace('\\', '\\\\')) for f in folders]))
        
    return (
        query
        .order_by(Media.file_created_at.asc())
        .limit(limit)
        .all()
    )
