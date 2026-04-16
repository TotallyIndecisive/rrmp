import { defineStore } from 'pinia'
import { library as libraryApi, playlists as playlistsApi } from '../services/api'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    tracks: [],
    folders: [],
    playlists: [],
    searchQuery: '',
  }),

  getters: {
    filteredTracks(state) {
      if (!state.searchQuery) return state.tracks
      
      const query = state.searchQuery.toLowerCase()
      return state.tracks.filter(track => 
        track.title?.toLowerCase().includes(query) ||
        track.artist?.toLowerCase().includes(query) ||
        track.album?.toLowerCase().includes(query)
      )
    },
  },

  actions: {
    setTracks(tracks) {
      this.tracks = tracks
    },

    setFolders(folders) {
      this.folders = folders
    },

    setPlaylists(playlists) {
      this.playlists = playlists
    },

    setSearch(query) {
      this.searchQuery = query
    },

    async fetchTracks() {
      try {
        const response = await libraryApi.getTracks()
        this.setTracks(response.data)
      } catch (error) {
        console.error('Failed to fetch tracks:', error)
      }
    },

    async fetchFolders() {
      try {
        const response = await libraryApi.getFolders()
        this.setFolders(response.data)
      } catch (error) {
        console.error('Failed to fetch folders:', error)
      }
    },

    async fetchPlaylists() {
      try {
        const response = await playlistsApi.getAll()
        this.setPlaylists(response.data)
      } catch (error) {
        console.error('Failed to fetch playlists:', error)
      }
    },

    async addFolder(path) {
      try {
        const response = await libraryApi.addFolder({ path })
        this.folders.push(response.data)
        return response.data
      } catch (error) {
        console.error('Failed to add folder:', error)
        throw error
      }
    },

    async deleteFolder(id) {
      try {
        await libraryApi.deleteFolder(id)
        this.folders = this.folders.filter(f => f.id !== id)
      } catch (error) {
        console.error('Failed to delete folder:', error)
        throw error
      }
    },

    async scanLibrary() {
      try {
        const response = await libraryApi.scanLibrary()
        await this.fetchTracks()
        return response.data
      } catch (error) {
        console.error('Failed to scan library:', error)
        throw error
      }
    },

    async createPlaylist(name) {
      try {
        const response = await playlistsApi.create(name)
        this.playlists.push(response.data)
        return response.data
      } catch (error) {
        console.error('Failed to create playlist:', error)
        throw error
      }
    },

    async deletePlaylist(id) {
      try {
        await playlistsApi.remove(id)
        this.playlists = this.playlists.filter(p => p.id !== id)
      } catch (error) {
        console.error('Failed to delete playlist:', error)
        throw error
      }
    },
  },
})