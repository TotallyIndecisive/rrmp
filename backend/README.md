# Backend Documentation

## Tech Stack

- FastAPI
- SQLAlchemy 2.0
- Alembic (migrations)
- SQLite
- python-vlc (audio playback)
- mutagen (metadata extraction)
- python-multipart (file uploads)

## Endpoints

- `GET /health` - Health check

### Library (`/library`)
- `POST /library/folders` - Add folder path
- `GET /library/folders` - List all folders
- `DELETE /library/folders/{folder_id}` - Remove folder
- `POST /library/scan` - Scan folders for audio files
- `GET /library/tracks` - List tracks with optional search filters
- `GET /library/recent` - Get 20 most recently played tracks

### Player (`/player`)
- `POST /player/play` - Play track by ID
- `POST /player/pause` - Pause playback
- `POST /player/resume` - Resume playback
- `POST /player/stop` - Stop playback
- `POST /player/seek` - Seek to position
- `POST /player/next` - Play next track
- `POST /player/previous` - Play previous track
- `POST /player/volume` - Set volume
- `GET /player/status` - Get playback status

### Playlists (`/playlists`)
- `POST /playlists` - Create playlist
- `GET /playlists` - List all playlists
- `GET /playlists/{playlist_id}` - Get playlist with tracks
- `DELETE /playlists/{playlist_id}` - Delete playlist
- `POST /playlists/{playlist_id}/tracks` - Add track to playlist
- `DELETE /playlists/{playlist_id}/tracks/{track_id}` - Remove track
- `PATCH /playlists/{playlist_id}/reorder` - Reorder tracks

### Metadata (`/metadata`)
- `GET /metadata/{track_id}` - Get track metadata with album art
- `PATCH /metadata/{track_id}/image` - Upload custom image
- `PATCH /metadata/{track_id}` - Update track info

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

### Queue Priority & Autoplay
- POST /player/queue endpoint accepts queue array and sets active queue
- queue_active boolean added to GET /player/status response
- Next/Previous priority: queue tracks first, then folder tracks
- Skips already-played tracks in current session
- Autoplay: VLC MediaPlayerEndReached event triggers next track logic
- Repeat all behavior at end of all tracks
- on_track_end callback handles autoplay logic

### Recent Tracks
- Added GET /library/recent endpoint returning 20 most recently played tracks
- Joins RecentlyPlayed with Track to return full track details ordered by played_at descending
- POST /player/play already inserts into RecentlyPlayed on every play (verified)

### Stage 5
- Player router fixed: proper queue initialization for next/previous track navigation
- Mock mode: graceful fallback when VLC libraries unavailable (still updates state)
- All player endpoints tested and working: play, pause, resume, stop, seek, next, previous, volume

### Stage 4
- CORS middleware: allows http://localhost:5173 with all methods/headers
- Static file serving: serves frontend/dist at root, SPA fallback for non-API routes
- FastAPI serves both API and built frontend from single port

### Stage 2
- Library router: folder management, recursive audio scanning with mutagen metadata extraction (.mp3, .flac, .wav, .ogg, .m4a)
- Player router: VLC singleton MediaPlayer with full playback control
- Playlists router: CRUD operations with track ordering
- Metadata router: track metadata with base64 album art, custom image uploads to backend/assets/images/
- Added python-multipart for file uploads
- All routers registered with API prefixes: /library, /player, /playlists, /metadata

### Stage 1
- Initial database setup with SQLite (rrmp.db)
- Created Track, Folder, Playlist, PlaylistTrack, RecentlyPlayed models
- Alembic initialized and initial migration applied
- `/health` endpoint added