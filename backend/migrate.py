from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE media ADD COLUMN IF NOT EXISTS source VARCHAR NOT NULL DEFAULT 'local'"))
    conn.execute(text("ALTER TABLE media DROP CONSTRAINT IF EXISTS uq_media_source_filepath"))
    conn.execute(text("ALTER TABLE media ADD CONSTRAINT uq_media_source_filepath UNIQUE (source, filepath)"))
    conn.commit()
    print('Migration successful!')
