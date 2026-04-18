import { defineStore } from 'pinia'
import { player as playerApi, library } from '../services/api'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    currentTrack: null,
    isPlaying: false,
    positionMs: 0,
    durationMs: 0,
    volume: 100,
    queue: [],
    queueIndex: -1,
    queueActive: false,
    shuffle: false,
    repeat: 'off',
    showQueue: false,
  }),

  getters: {
    queueActive: (state) => state.queueActive,
  },

  actions: {
    setTrack(track) {
      this.currentTrack = track
      if (track) {
        this.durationMs = track.duration ? track.duration * 1000 : 0
      }
    },

    setPlaying(playing) {
      this.isPlaying = playing
    },

    updatePosition(positionMs) {
      this.positionMs = positionMs
    },

    updateStatus(status) {
      if (status.track_id && (!this.currentTrack || this.currentTrack.id !== status.track_id)) {
      }
      this.isPlaying = status.is_playing
      this.positionMs = status.position_ms
      this.durationMs = status.duration_ms
      this.volume = status.volume
      this.shuffle = status.shuffle
      this.repeat = status.repeat
      this.queueActive = status.queue_active
    },

    setQueue(queue, index = 0) {
      this.queue = queue
      this.queueIndex = index
    },

    async playTrack(track) {
      try {
        console.log('player.js: Calling playerApi.play with track_id:', track.id)
        const response = await playerApi.play(track.id)
        console.log('player.js: API response:', response.data)
        this.setTrack(track)
        this.setPlaying(true)
        console.log('player.js: Track set, isPlaying:', this.isPlaying)
      } catch (error) {
        console.error('player.js: Failed to play track:', error)
      }
    },

    async pause() {
      try {
        await playerApi.pause()
        this.setPlaying(false)
      } catch (error) {
        console.error('Failed to pause:', error)
      }
    },

    async resume() {
      try {
        await playerApi.resume()
        this.setPlaying(true)
      } catch (error) {
        console.error('Failed to resume:', error)
      }
    },

    async stop() {
      try {
        await playerApi.stop()
        this.setTrack(null)
        this.setPlaying(false)
        this.positionMs = 0
      } catch (error) {
        console.error('Failed to stop:', error)
      }
    },

    async seek(positionMs) {
      try {
        await playerApi.seek(positionMs)
        this.positionMs = positionMs
      } catch (error) {
        console.error('Failed to seek:', error)
      }
    },

    async nextTrack() {
      try {
        console.log('player.js: Calling playerApi.next()')
        const response = await playerApi.next()
        console.log('player.js: Next response:', response.data)
        if (response.data.track_id) {
          if (response.data.queue_active) {
            this.queueIndex = Math.min(this.queueIndex + 1, this.queue.length - 1)
          } else {
            this.queueIndex = -1
          }
          this.queueActive = response.data.queue_active
          const trackResponse = await library.getTracks()
          const track = trackResponse.data.find(t => t.id === response.data.track_id)
          if (track) {
            this.setTrack(track)
            this.setPlaying(true)
          }
        }
      } catch (error) {
        console.error('player.js: Failed to play next:', error)
      }
    },

    async previousTrack() {
      try {
        console.log('player.js: Calling playerApi.previous()')
        const response = await playerApi.previous()
        console.log('player.js: Previous response:', response.data)
        if (response.data.track_id) {
          this.queueActive = response.data.queue_active
          const trackResponse = await library.getTracks()
          const track = trackResponse.data.find(t => t.id === response.data.track_id)
          if (track) {
            this.setTrack(track)
            this.setPlaying(true)
          }
        }
      } catch (error) {
        console.error('player.js: Failed to play previous:', error)
      }
    },

    async setVolume(level) {
      try {
        await playerApi.setVolume(level)
        this.volume = level
      } catch (error) {
        console.error('Failed to set volume:', error)
      }
    },

    async fetchStatus() {
      try {
        const response = await playerApi.getStatus()
        this.updateStatus(response.data)
      } catch (error) {
        console.error('Failed to fetch status:', error)
      }
    },

    async toggleShuffle() {
      try {
        const response = await playerApi.toggleShuffle()
        this.shuffle = response.data.shuffle
      } catch (error) {
        console.error('Failed to toggle shuffle:', error)
      }
    },

    async cycleRepeat() {
      try {
        const response = await playerApi.cycleRepeat()
        this.repeat = response.data.repeat
      } catch (error) {
        console.error('Failed to cycle repeat:', error)
      }
    },

    setShowQueue(value) {
      this.showQueue = value
    },

    toggleQueue() {
      this.showQueue = !this.showQueue
    },

    clearQueue() {
      this.queue = []
      this.queueIndex = -1
      this.queueActive = false
      this.syncQueueToBackend()
    },

    removeFromQueue(index) {
      if (index < 0 || index >= this.queue.length) return
      this.queue.splice(index, 1)
      if (index < this.queueIndex) {
        this.queueIndex--
      } else if (index === this.queueIndex && this.queue.length > 0) {
        this.queueIndex = Math.min(this.queueIndex, this.queue.length - 1)
      } else if (this.queueIndex >= this.queue.length) {
        this.queueIndex = this.queue.length - 1
      }
    },

    async playFromQueue(index) {
      if (index < 0 || index >= this.queue.length) return
      const track = this.queue[index]
      this.queueIndex = index
      await this.playTrack(track)
    },

    addToQueue(track) {
      const exists = this.queue.some(t => t.id === track.id)
      if (exists) {
        return { duplicate: true, title: track.title }
      }
      this.queue.push(track)
      this.syncQueueToBackend()
      return { duplicate: false, title: track.title }
    },

    async syncQueueToBackend() {
      try {
        await playerApi.setQueue(this.queue)
      } catch (error) {
        console.error('Failed to sync queue to backend:', error)
      }
    },
  },
})