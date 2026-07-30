# Smart Media Assistant - Project Context

## 1. Project Overview
The **Smart Media Assistant** is an intelligent, voice-activated media management platform designed to revolutionize how users interact with their media libraries. It integrates Large Language Models (LLMs) via Groq, local speech recognition via OpenAI Whisper, and cloud storage integrations like Google Drive. The goal is to provide a hands-free, intuitive, and highly responsive experience for querying, organizing, and playing media files (videos, images, audio).

## 2. System Architecture
The system follows a decoupled Client-Server architecture:
- **Frontend (React + Vite)**: A dynamic, visually stunning user interface that captures user voice input and plays media.
- **Backend (FastAPI, Python)**: The central hub handling API requests, file scanning, and AI intent parsing. 
- **Database (SQLite/PostgreSQL)**: A highly performant local indexing system that stores metadata for local and cloud files without duplicating or moving the physical files.

## 3. Core Workflows
### 3.1 Media Scanning (Local & Cloud)
- **Local Scanning**: The backend recursively traverses a target directory (`MEDIA_ROOT`), applying a cheap-to-expensive cascade of checks (MIME sniffing -> EXIF extraction -> `ffmpeg`/`mutagen` for duration) to categorize files as short/long audio, video, or image.
- **Google Drive Integration**: Utilizes strict PKCE-secured OAuth 2.0 to scan a user's Google Drive and persist unified metadata alongside local files.

### 3.2 Voice Command Workflow
1. **Capture**: Frontend records audio via Web Audio API.
2. **Transcription**: Backend converts audio to text instantly via local Whisper model.
3. **Intent Parsing**: The text is sent to an LLM (e.g., Groq Llama 3) to generate a structured JSON payload defining the user's intent.
4. **Execution & Playback**: The backend's Query Engine interprets the intent, builds the necessary database query, and returns media URLs for the frontend to play.

## 4. Backend Capabilities & Structure (Local Disk MVP)
Located in the `backend/` directory, the FastAPI application features:
- **Demo Mode**: Endpoints to seed fake data (`POST /demo/seed`) allowing testing of the natural language pipeline (`POST /command`) without real media.
- **Key Modules**:
  - `classifier.py` / `scanner.py`: Local scanning logic.
  - `gdrive_scanner.py`: Google Drive logic.
  - `intent_parser.py`: A swappable text-to-intent engine (currently simple keyword matching, to be upgraded to LLM).
  - `query_engine.py`: Ordering/mixing logic for retrieving media (e.g., shortest-first, 3-short-1-long mix).

**Backend Setup** (Windows):
1. Install ffmpeg: `winget install ffmpeg`
2. Python venv setup: `python -m venv venv`, `venv\Scripts\activate`, `pip install -r requirements.txt` (and `pip install python-magic-bin`).
3. Setup `.env` with `DATABASE_URL` and `MEDIA_ROOT`.
4. Run: `uvicorn app.main:app --reload`

## 5. Frontend Capabilities
Located in the `frontend/` directory, currently structured as a React + Vite application ready to be developed into a rich UI.
- **Key Technologies**: React, Vite, styling (TailwindCSS/Vanilla CSS).
- **Next Steps**: Wire up audio capture, connect to the backend API (`/command`), and build a seamless media player component.

**Frontend Setup**:
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## 6. Current State & Next Steps
- **Completed**: Foundation setup, backend scanning logic, database schema, demo seeding, and basic API endpoints.
- **Pending Implementation**: 
  - Integrating Groq API strictly into `intent_parser.py` for advanced natural language understanding.
  - Finishing the SQL query engine for complex playlist assemblies.
  - Building the frontend microphone UI and media player components to fully realize the end-to-end voice-controlled experience.
