# RetroReel MP

A retro-themed media player for music collections.

## Tech Stack

- **Frontend**: Vue 3, Vite, Tailwind CSS, Pinia, axios, vuedraggable
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Database**: SQLite
- **Audio**: python-vlc, mutagen

## Prerequisites

- Python 3.10+
- Node.js 18+
- uv (package manager)
- npm (package manager)
- VLC system libraries (for audio playback)

## Setup

### Backend
- `uv sync`
- `uv run alembic upgrade head`
- `uv run python run.py`

### Frontend
- `cd frontend && npm install`
- `npm run dev`

## Changelog

### Stage 5 Fixes
- Fix add track to playlist: confirmed backend schema and frontend payload match, API working correctly
- Fix NowPlaying not updating on next/previous: player store now fetches full track info after next/previous calls and updates currentTrack reactively

### Stage 5
- Production build: `npm run build` creates optimized frontend in frontend/dist/
- Standalone app: `uv run python run.py` starts server + opens native window (fallback to browser if pywebview unavailable)
- Full integration: All frontend and backend fully connected via FastAPI static file serving

### Stage 4
- Backend: CORS middleware for http://localhost:5173, static file serving from frontend/dist
- Frontend build: Production build with `npm run build`, served by FastAPI at root
- Standalone: `run.py` launches uvicorn in background thread, waits for /health, opens pywebview (falls back to browser)
- Error handling: try/catch on all API calls, toast notifications for errors and success events
- Metadata editing: track title/artist/album editing, custom image upload

### Stage 3
- Vue 3 + Vite frontend setup with Tailwind CSS retro theme
- Retro color palette: amber, cream, brown, dark tones
- Pinia stores for player state and library management
- Components: NowPlaying (cassette visualization), PlayerControls, Library, Playlist, FolderManager
- API service layer with axios
- Three-column layout: Library | NowPlaying | Playlist
- Vite dev server with proxy to backend

### Stage 2
- Library router: folder management and recursive audio scanning with mutagen metadata extraction
- Player router: VLC-based playback control (play, pause, resume, stop, seek, next, previous, volume)
- Playlists router: full CRUD with track ordering support
- Metadata router: track info retrieval with embedded album art, custom image upload
- Pydantic schemas for all request/response models
- 21 API endpoints total

### Stage 1
- Project initialization with FastAPI backend
- SQLite database setup with SQLAlchemy ORM
- Five models: Track, Folder, Playlist, PlaylistTrack, RecentlyPlayed
- Alembic migrations configured and applied
- `/health` endpoint implemented