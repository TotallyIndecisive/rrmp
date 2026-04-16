# RetroReel MP

A retro-themed media player for music collections.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Database**: SQLite
- **Audio**: python-vlc, mutagen

## Prerequisites

- Python 3.10+
- uv (package manager)

## Setup

- `uv sync`
- `uv run alembic upgrade head`
- `uv run python run.py`

## Changelog

### Stage 1
- Project initialization with FastAPI backend
- SQLite database setup with SQLAlchemy ORM
- Five models: Track, Folder, Playlist, PlaylistTrack, RecentlyPlayed
- Alembic migrations configured and applied
- `/health` endpoint implemented