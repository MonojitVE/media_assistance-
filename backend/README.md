# Media Assistant Backend (MVP — Local Disk)

## What this does
Scans a local folder, classifies every image/video/audio file using a
cheap-to-expensive cascade (MIME sniff -> EXIF -> filename heuristics ->
ffprobe/mutagen for duration), and stores the result in Postgres. The
database *is* your folder system — physical files never get moved or
copied, we just tag them.

## Setup (Windows / PowerShell)

1. Install ffmpeg (needed for ffprobe):
   ```powershell
   winget install ffmpeg
   ```

2. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Note: `python-magic` on Windows also needs `python-magic-bin`:
   ```powershell
   pip install python-magic-bin
   ```

3. Copy `.env.example` to `.env` and fill in:
   - `DATABASE_URL` — your Neon Postgres connection string
   - `MEDIA_ROOT` — the folder you want scanned (e.g. `C:/Users/you/Pictures`)

4. Run the server:
   ```powershell
   uvicorn app.main:app --reload
   ```

5. Trigger a scan:
   ```
   POST http://localhost:8000/scan
   ```
   (Optionally pass `?root=C:/some/other/folder` to override MEDIA_ROOT for one run)

6. Query results:
   ```
   GET http://localhost:8000/media?type=video&subtype=short
   GET http://localhost:8000/media/stats
   ```

## Demo mode (no real files needed)

For a pitch/demo, you don't need to point this at real media at all:

1. Run the server: `uvicorn app.main:app --reload`
2. Seed fake data: `POST /demo/seed` — creates a realistic mix of short/long
   videos, short/long audio, photos, and screenshots with randomized
   durations and dates.
3. Run commands against it:
   ```
   POST /command   { "text": "show me mix videos" }
   POST /command   { "text": "play short audio" }
   POST /command   { "text": "show my screenshots" }
   POST /command   { "text": "play long videos" }
   ```
   Each returns the parsed intent AND the correctly ordered/mixed playlist
   — this is the exact logic that would drive the display once the
   voice/frontend layer is wired in.
4. Reset anytime: `DELETE /demo/clear`

This proves the core value prop — natural command in, correctly assembled
playlist out — entirely at the API level, so you can demo it with just
curl, Postman, or Swagger UI (`/docs`) before any frontend exists.

## What's NOT built yet (next steps)
- The query engine for voice-command patterns (shortest->longest ordering,
  3-short-1-long mixed playback) — this needs custom SQL, not just filters
- Voice intent parsing (transcript -> structured command)
- The frontend mic/display UI
- Google Drive source (local disk only for now)

## Project structure
```
app/
  main.py          FastAPI app + router registration
  config.py        Settings loaded from .env
  database.py      SQLAlchemy engine/session
  models.py        Media table definition
  schemas.py       Pydantic response models
  classifier.py    The classification cascade
  scanner.py       Walks MEDIA_ROOT, upserts into DB
  query_engine.py  Ordering/mixing logic (shortest-first, 3-short-1-long mix)
  intent_parser.py Keyword-based text -> structured intent (voice-command stand-in)
  routers/
    scan.py        POST /scan
    media.py       GET /media, GET /media/stats
    command.py     POST /command  (text in -> intent + playlist out)
    demo.py        POST /demo/seed, DELETE /demo/clear
```

## Note on the intent parser
`intent_parser.py` uses simple keyword matching so the demo works with zero
external API keys. It's intentionally swappable — replace `parse_command()`
with an LLM function-calling call (Claude/GPT) later for real natural-language
robustness; the rest of the pipeline (`command.py`, `query_engine.py`)
doesn't need to change since it only consumes the structured intent dict.
