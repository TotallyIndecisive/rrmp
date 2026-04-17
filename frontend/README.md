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

## Changelog

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