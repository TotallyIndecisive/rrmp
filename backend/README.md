# Backend Documentation

## Tech Stack

- FastAPI
- SQLAlchemy 2.0
- Alembic (migrations)
- SQLite

## Endpoints

- `GET /health` - Health check

## Database Models

- `Track` - Music track metadata
- `Folder` - Monitored folder paths
- `Playlist` - User playlists
- `PlaylistTrack` - Playlist-track associations
- `RecentlyPlayed` - Playback history

## Migrations

- Run `uv run alembic upgrade head` to apply migrations
- Run `uv run alembic revision --autogenerate -m "message"` to create new migration

## Changelog

### Stage 1
- Initial database setup with SQLite (rrmp.db)
- Created Track, Folder, Playlist, PlaylistTrack, RecentlyPlayed models
- Alembic initialized and initial migration applied
- `/health` endpoint added