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

### Stage 3
- Initial Vue 3 frontend setup
- Retro cassette-themed UI with Tailwind CSS
- All core components implemented
- Pinia state management
- API service layer
- Three-column responsive layout