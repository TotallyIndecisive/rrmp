import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const library = {
  getFolders: () => api.get('/library/folders'),
  addFolder: (path) => api.post('/library/folders', { path }),
  deleteFolder: (id) => api.delete(`/library/folders/${id}`),
  scanLibrary: () => api.post('/library/scan'),
  getTracks: (params) => api.get('/library/tracks', { params }),
}

export const player = {
  play: (trackId) => api.post('/player/play', { track_id: trackId }),
  pause: () => api.post('/player/pause'),
  resume: () => api.post('/player/resume'),
  stop: () => api.post('/player/stop'),
  seek: (positionMs) => api.post('/player/seek', { position_ms: positionMs }),
  next: () => api.post('/player/next'),
  previous: () => api.post('/player/previous'),
  setVolume: (level) => api.post('/player/volume', { level }),
  getStatus: () => api.get('/player/status'),
}

export const playlists = {
  getAll: () => api.get('/playlists'),
  getOne: (id) => api.get(`/playlists/${id}`),
  create: (name) => api.post('/playlists', { name }),
  remove: (id) => api.delete(`/playlists/${id}`),
  addTrack: (playlistId, trackId) => api.post(`/playlists/${playlistId}/tracks`, { track_id: trackId }),
  removeTrack: (playlistId, trackId) => api.delete(`/playlists/${playlistId}/tracks/${trackId}`),
  reorder: (playlistId, trackIds) => api.patch(`/playlists/${playlistId}/reorder`, { track_ids: trackIds }),
}

export const metadata = {
  getMetadata: (trackId) => api.get(`/metadata/${trackId}`),
  updateImage: (trackId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.patch(`/metadata/${trackId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  updateTrack: (trackId, data) => api.patch(`/metadata/${trackId}`, data),
}

export default api