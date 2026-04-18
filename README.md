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

### Panel Scrolling & Viewport Lock
- Fixed player controls being pushed off screen when Library folders expand
- Root layout: `height: 100vh`, `max-height: 100vh`, `overflow: hidden`, `display: flex`, `flex-direction: column`
- Header: fixed 52px height with `flex-shrink: 0`
- Main content: `flex: 1`, `min-height: 0` — critical for flex children not to overflow viewport
- PlayerControls: fixed 80px height with `flex-shrink: 0`, always stays at bottom
- Library panel: container `height: 100%`, `overflow: hidden`, header `flex-shrink: 0`, track list `flex: 1`, `min-height: 0`, `overflow-y: auto`
- Playlist panel: same layout fix as Library
- Queue panel: same layout fix, side drawer scrolls internally
- NowPlaying: `height: 100%`, `overflow: hidden`, stays centered
- Retro scrollbar styling: 6px width, amber (#F5A623) thumb, dark (#1C1009) track, hover brightens to #FFB84D

### Playlist Management Fixes
- Backend: Added debug logging to `POST /playlists/{playlist_id}/tracks` for troubleshooting
- Backend: Added debug logging to `DELETE /playlists/{playlist_id}/tracks/{track_id}`
- Frontend Library: Added console logs on add-to-playlist button click, improved error handling
- Frontend Library: Added toast notification "Added to playlist: {playlist name}" on success
- Frontend Library: Added error toast on failure, refreshes playlist list after add
- Frontend Playlist: Track count badge now uses playlist.trackCount, updates on add/remove
- Frontend Playlist: Fixed track display issue - added explicit `style="display: block; overflow: visible;"` to playlist-tracks container
- Frontend Playlist: Fixed play button - now uses `setQueue(queueTracks, 0)` then `playTrack(firstTrack)` and syncs to backend
- Frontend Playlist: Added console logs to playPlaylist and fetchPlaylistTracks for debugging
- Frontend Playlist: Added duration display to each track row
- Frontend Playlist: Added play button to each playlist (plays all tracks in order via queue)
- Frontend Playlist: Added toast "Playing: {playlist name}" on play
- Frontend Playlist: Added toast "Removed from playlist" on track removal
- Frontend Playlist: Added toast "Playlist deleted" on playlist deletion
- Added toast notifications for all playlist operations

### Library Autoplay (Folder Tracks Only)
- VLC MediaPlayerEndReached event triggers autoplay for folder tracks only
- Uses threading.Timer(1.0, _play_next_library_track) to avoid deadlock
- Skips entirely if queue_active is true (queue logic untouched)
- Sequential folder playback, shuffle mode, repeat all behavior
- Stops on last track if repeat is off

### Reliable Autoplay
- VLC MediaPlayerEndReached event triggers autoplay callback on track end
- Uses threading.Timer(0.5, _play_next_track) to avoid VLC deadlock
- _play_next_track() calls shared logic, works identically to POST /player/next
- Works in normal mode (sequential), shuffle mode (random), and with queue

### Mini Player Mode
- Added toggle button in header to switch between full and mini view
- Mini mode: hides Library and Playlist panels, NowPlaying scaled down to 50%
- PlayerControls remains visible at bottom
- POST /window/resize endpoint calls webview.windows[0].resize(width, height)
- Mini mode resizes to 480x200, full mode restores 1280x800

### Shared Next Track Logic
- Extracted next track priority logic into single `_get_next_track_id()` function
- Both POST /player/next and on_track_end (autoplay) now call shared function
- Ensures identical behavior for manual next and autoplay
- Added `_play_track()` helper for consistent track playback
- on_track_end now properly transitions from queue to folder in shuffle mode

### Shuffle Bug Fix & Queue Verification
- Fixed shuffle repeating last two songs bug
- Added `_played_folder_tracks` set to track all played folder tracks
- Added `reset_played_tracks()` helper function to clear history
- Reset played tracks on: manual track play, stop, clear queue
- Every track added to played set before next random selection
- When all folder tracks played, history resets for fresh shuffle
- Verified all 7 queue scenarios work correctly

### Shuffle Queue Fix
- Shuffle mode now follows same queue priority rules as normal mode
- Queue always plays sequentially in order — shuffle never applies to queue
- Shuffle only applies to folder fallback after queue is exhausted
- Fixed: POST /player/next, on_track_end, POST /player/previous all respect queue-first rule

### Queue Priority & Autoplay
- POST /player/queue syncs frontend queue to backend
- queue_active state reflects whether queue has unplayed tracks
- Priority order: queue tracks first, then folder tracks, skipping already played
- Autoplay: VLC fires MediaPlayerEndReached, triggers next track automatically
- Queue panel: played tracks dimmed, "Queue finished — continuing from library" label
- Amber indicator on queue button when active

### Queue Feature
- Add to Queue button on each track row in Library (next to Add to Playlist)
- Appends track to end of queue, newest at bottom
- Duplicate detection with toast notification "{title} is already in the queue"
- Success toast "Added to queue: {title}"
- Queue panel: side drawer overlay, displays tracks in order added
- Per-track remove from queue and clear queue buttons
- Currently playing track highlighted in amber

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