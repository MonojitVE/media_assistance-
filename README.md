# Smart Media Assistant

A full-stack AI-powered media management app that lets users browse, filter, and command media libraries using natural-language prompts. The project combines a React frontend, a FastAPI backend, and metadata-driven media classification to support both local folders and Google Drive content in one unified experience.

This project was built as a portfolio piece to demonstrate end-to-end product thinking, backend engineering, AI integration, and UI design in a real-world media workflow.

## Why this project

Modern media libraries are fragmented across local disks, cloud storage, and folders with inconsistent naming. Users often spend too much time manually browsing and organizing files instead of focusing on what they actually want to watch, listen to, or review.

Smart Media Assistant addresses that by:

- indexing media from local folders and Google Drive
- classifying content by type and subtype
- surfacing smart stats and folder-level browsing
- interpreting simple voice/text commands like “show me short videos” or “play long audio”
- returning curated playlist results from a structured media database

## Key features

### Media ingestion and classification
- recursive local folder scanning
- support for images, videos, and audio files
- metadata extraction using MIME checks, image EXIF, ffprobe, and Mutagen
- automatic classification into categories such as:
  - image: photo, screenshot, whatsapp
  - video: short, long
  - audio: short, long

### Google Drive integration
- OAuth 2.0 login flow for Google Drive
- Drive scanning and ingestion into the same media index
- backend-proxied file access for files stored in Drive
- disconnect flow to remove Drive-scanned entries and stored token data

### AI-driven command processing
- natural-language command parsing via Groq/OpenAI-compatible API
- structured intent extraction with a typed schema
- conversion of user text into actions such as:
  - play
  - slideshow
  - explore
  - unknown
- query engine that builds ordered or mixed media playlists

### Frontend experience
- React + Vite interface for media browsing and folder filtering
- interactive media explorer with folder selection and smart categories
- media display states for playback and slideshow actions
- Google Drive connect/disconnect controls

## Architecture

The project follows a lightweight client-server architecture:

- Frontend: React, Vite, Framer Motion, Lucide
- Backend: FastAPI, SQLAlchemy, PostgreSQL-ready data model
- Database: relational metadata store for file indexing
- AI layer: Groq/OpenAI-style structured intent parser
- Integrations: Google Drive API and local filesystem scanning

## Project structure

```text
media_assistance/
├── backend/
│   ├── app/
│   │   ├── classifier.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── gdrive_scanner.py
│   │   ├── intent_parser.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── organizer.py
│   │   ├── query_engine.py
│   │   ├── scanner.py
│   │   ├── schemas.py
│   │   └── routers/
│   │       ├── command.py
│   │       ├── demo.py
│   │       ├── drive.py
│   │       ├── media.py
│   │       └── scan.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── context.md
├── proposal.md
├── render.yaml
├── .gitignore
├── .python-version
└── README.md
```

## Core backend modules

### app/main.py
Initializes the FastAPI app, applies CORS, and registers all API routers.

### app/models.py
Defines the SQLite/PostgreSQL-ready Media table used to store file metadata, type, subtype, and timestamps.

### app/classifier.py
Performs content classification by analyzing file type and metadata to assign:
- image vs video vs audio
- short vs long media
- photo vs screenshot vs whatsapp-oriented tags

### app/scanner.py
Walks a target folder recursively and indexes supported files while avoiding duplicates.

### app/query_engine.py
Builds query results for playback, sorting, and playlist generation logic.

### app/intent_parser.py
Converts natural-language commands into a structured JSON intent compatible with the app's downstream logic.

### app/gdrive_scanner.py
Scans Google Drive files and stores their metadata in the same database model.

### app/routers/
Handles route-specific functionality for:
- scanning media
- retrieving media metadata and stats
- natural-language execution
- demo seeding
- Drive OAuth and disconnect flow

## Example user flows

### Local media discovery
1. User selects a folder to scan.
2. Backend walks the directory and classifies files.
3. Metadata is saved in the database.
4. Frontend displays folder stats and smart categories.

### Command execution
Example request:

```json
{
  "text": "show me 3 short videos and 1 long video",
  "folders": ["C:/Users/name/Pictures"]
}
```

The backend parses the request into an intent and returns a curated playlist from the indexed media records.

### Google Drive integration
1. User clicks Connect Google Drive.
2. OAuth flow redirects to Google.
3. Backend exchanges token and scans Drive files.
4. Files appear in the same media catalog as local content.

## Tech stack

### Frontend
- React
- Vite
- Framer Motion
- Lucide React

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Data and AI
- PostgreSQL-compatible SQL schema
- Groq/OpenAI-style structured LLM parsing
- ffprobe and Mutagen for media analysis
- Google OAuth and Drive API integration

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- ffmpeg installed and available on PATH

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create an environment file with your project settings, including database and optional Google credentials.

Then start the app:

```bash
uvicorn app.main:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## API highlights

### Media endpoints
- GET /media
- GET /media/stats
- GET /media/folders
- GET /media/file/{media_id}

### Scan endpoints
- POST /scan
- POST /scan/organize

### Command endpoints
- POST /command

### Demo endpoints
- POST /demo/seed
- DELETE /demo/clear

### Drive endpoints
- GET /drive/auth/url
- POST /drive/auth/token
- POST /drive/scan
- POST /drive/disconnect

## Portfolio positioning

This project demonstrates:

- product design thinking for a consumer-facing media workflow
- full-stack engineering across frontend and backend
- database modeling and query design
- practical AI integration using structured outputs
- external API integration with OAuth and cloud storage
- end-to-end user experience from command input to media playback results

## What I learned

This project taught me how to connect AI, real-world data pipelines, and polished UX into a single usable product. It reinforced the importance of designing for real user intent, being careful with data modeling, and understanding how metadata can become a strong foundation for intelligent media experiences.

## Future improvements

- replace keyword-based intent parsing with an LLM-powered pipeline using robust schema validation
- expand media search to semantic and visual matching
- add user authentication and multi-user support
- improve playlist personalization and recommendation logic
- build a richer mobile-friendly UI and better media playback controls
- add automated tests for backend routes and classification logic

## License

This project is for portfolio and learning purposes. Please contact the author before using it commercially.

---

Built as a practical AI + media application prototype to explore how intelligent interfaces can simplify real-world content organization and retrieval.
