# Frontend Documentation

## Tech Stack

- Vue 3 (Composition API)
- Vite (build tool)
- Tailwind CSS v4 (styling)
- Pinia (state management)
- axios (HTTP client)
- vuedraggable (drag and drop)

## Retro Theme

- **Colors**: retro-amber (#F5A623), retro-cream (#F5F0E8), retro-brown (#3E2723), retro-dark (#1C1009), retro-warm (#8D6E63)
- **Font**: Space Mono (Google Fonts)

## Setup

- `npm install`
- `npm run dev` (starts on http://localhost:5173)
- `npm run build` (production build)

## Project Structure

```
src/
├── components/
│   ├── NowPlaying.vue      # Cassette visualization with spinning reels
│   ├── PlayerControls.vue  # Bottom playback controls bar
│   ├── Library.vue         # Left sidebar track list
│   ├── Playlist.vue        # Right sidebar playlist management
│   └── FolderManager.vue   # Modal for folder management
├── services/
│   └── api.js             # Axios API client
├── stores/
│   ├── player.js          # Player state (Pinia)
│   └── library.js         # Library state (Pinia)
├── App.vue                 # Main layout
└── main.js                # App entry point
```

## Components

### NowPlaying
- Cassette tape visual with animated spinning reels
- Album art display from embedded or custom image
- Track info: title, artist, album

### PlayerControls
- Play/pause, stop, next, previous buttons
- Seek bar with position tracking
- Volume slider
- Retro-styled counter display
- Polls `/player/status` every second

### Library
- Track list with search filtering
- Click to play
- Add track to playlist
- Folder management button

### Playlist
- Create/delete playlists
- Expand to see tracks
- Drag-and-drop reorder (vuedraggable)
- Remove tracks from playlist

### FolderManager
- Add/remove folder paths
- Scan library button
- Displays scan results

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Toggle play/pause |
| `ArrowRight` | Seek forward 10 seconds |
| `ArrowLeft` | Seek backward 10 seconds |
| `ArrowUp` | Volume up 10% |
| `ArrowDown` | Volume down 10% |
| `N` | Next track |
| `P` | Previous track |
| `S` | Toggle shuffle |
| `R` | Cycle repeat (off → one → all → off) |
| `M` | Mute/unmute toggle |

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
- Folder dropdowns in Library with chevron animation, track count badges, play all button
- Tracks grouped by folder_path with collapsible sections

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

### UI Polish & Animations
- Added fade transition when track changes in NowPlaying.vue (Transition mode="out-in")
- Added tape grain texture overlay using SVG noise pattern pseudo-element
- Added VU meter in PlayerControls: 5 vertical bars with bounce animation while playing
- Added hover transitions to all buttons: scale up + amber glow effect
- Added smooth slide-in animation for toast notifications (translateX from right)
- Added pulsing amber border animation for currently playing track in Library
- Added prefers-reduced-motion media query support to disable animations

### NowPlaying Fix
- Fixed NowPlaying display missing after theme toggle implementation
- Added missing imports: ref, watch, onMounted, metadata API to NowPlaying.vue
- Added missing album art fetch logic with watch on currentTrack
- NowPlaying cassette, reels, track info, and album art now display correctly

### Dark/Light Theme Toggle
- Added theme toggle button in header (sun/moon icon)
- Created theme.js Pinia store with localStorage persistence
- Updated tailwind.config.js with darkMode: 'class'
- Updated App.vue, Library, Playlist, NowPlaying, PlayerControls with theme-aware classes
- Dark: retro-dark background, retro-cream text, retro-amber accents
- Light: retro-cream background, retro-brown text, retro-amber accents

### Reliable Autoplay (Backend)
- VLC MediaPlayerEndReached event triggers autoplay via threading.Timer
- Uses 0.5s delay to avoid VLC callback deadlock
- _play_next_track() mirrors POST /player/next logic exactly
- Works in normal, shuffle, and queue modes

### Mini Player Mode
- Added toggle button (Mini/Full) in header to switch between views
- Mini mode: hides Library and Playlist panels, NowPlaying scaled to 50%
- PlayerControls remains visible at bottom
- Calls POST /window/resize endpoint with 480x200 for mini, 1280x800 for full
- Toast notifications confirm mode switch

### Shared Next Track Logic (Backend)
- Extracted next track priority into single `_get_next_track_id()` function
- Both POST /player/next and on_track_end call shared function
- on_track_end now correctly transitions from queue to folder in shuffle mode
- Autoplay follows same behavior as manual next button

### Shuffle Bug Fix & Queue Verification
- Fixed shuffle repeating last two songs bug
- Backend tracks all played folder tracks in session
- Reset played tracks on manual track select, stop, clear queue
- All queue scenarios verified: add, playback order, autoplay, folder fallback, shuffle mode, clear mid-playback, manual track click

### Shuffle Queue Fix
- Shuffle mode now follows same queue priority rules as normal mode
- Queue always plays sequentially in order — shuffle never applies to queue
- Shuffle only applies to folder fallback after queue is exhausted

### Queue Priority & Autoplay
- Added queueActive state synced from backend GET /player/status
- POST /player/queue endpoint syncs queue from frontend to backend
- Priority: queue tracks first, then folder tracks, skipping already played
- Currently playing track in amber, played tracks dimmed
- "Queue finished — continuing from library" label when queue exhausted
- Amber indicator dot on queue button when queue_active is true
- Clear queue syncs empty array to backend

### Queue Panel (Updated)
- Removed drag-and-drop reordering
- Add to Queue button on each track row in Library (list icon, same styling as Add to Playlist)
- Clicking appends track to end of queue, newest at bottom
- Duplicate detection: shows toast "{title} is already in the queue" if already in queue
- Success toast: "Added to queue: {title}"
- Queue displays tracks in order added (newest at bottom)
- Currently playing track highlighted in amber
- Per-track remove from queue button
- Clear queue button
- Scrollable list when many tracks

### Queue Panel
- Created Queue.vue component with ordered list of tracks
- Currently playing track highlighted in amber
- Drag-and-drop reordering using vuedraggable
- Clear queue button to remove all tracks
- Per-track remove from queue button
- Toggle button in PlayerControls (list icon) shows/hides side drawer overlay
- Wired to player store queue array

### Recently Played
- Added collapsible Recently Played section in Library panel below main track list
- Fetches from GET /library/recent on expand, lazy-loaded
- Displays last 20 tracks with title, artist, and duration
- Clicking a track plays it same way as main library
- Retro cassette theme styling consistent with rest of Library

### Keyboard Shortcuts
- Global keyboard shortcut listeners on document
- Space toggles play/pause
- Arrow keys for seek and volume
- N/P for next/previous track
- S toggle shuffle, R cycle repeat
- M mute/unmute
- Prevent default browser behavior for all shortcuts
- Retro toast notifications showing action triggered (+10s, -10s, Shuffle ON, etc.)
- Listeners removed on component unmount

### Shuffle/Repeat
- Added shuffle button: toggles random playback mode, POST /player/shuffle, visual state from poll
- Added repeat button: cycles off → one → all → off, POST /player/repeat, visual indicators (amber when active, "1" for one)
- Added shuffle/repeat fields to player store state and updateStatus action
- Added toggleShuffle() and cycleRepeat() actions to player store
- Added toggleShuffle/cycleRepeat to API service
- Retro-styled buttons matching cassette theme

### Stage 5 Fixes
- Fixed NowPlaying not updating on next/previous: player store now fetches full track info (title, artist, album) via library.getTracks() after next/previous API calls and updates currentTrack reactively so NowPlaying display updates immediately
- Added console logging to track add to playlist flow for debugging

### Stage 5
- Build verification: `npm run build` completes successfully
- API proxy: requests to `/api/*` forwarded to backend (via vite.config.js)
- Full integration: All components communicate with backend via axios

### Stage 4
- Toast notification system: amber background, brown text, Space Mono font
- Error handling: try/catch wrapped on all API calls
- Success notifications: scan complete, playlist created, track added
- Metadata editing: title, artist, album fields editable
- Custom image upload: file input that updates track artwork
- Debounced search: 300ms delay on library search
- Queue management: click track sets full track list as queue

### Stage 3
- Initial Vue 3 frontend setup
- Retro cassette-themed UI with Tailwind CSS
- All core components implemented
- Pinia state management
- API service layer
- Three-column responsive layout