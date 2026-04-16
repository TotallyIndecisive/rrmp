# RetroReel MP

A retro-themed media player for music collections.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Database**: SQLite
- **Audio**: python-vlc, mutagen

## Prerequisites

- Python 3.10+
- uv (package manager)
- VLC system libraries (for audio playback)

## Setup

- `uv sync`
- `uv run alembic upgrade head`
- `uv run python run.py`

## Changelog

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