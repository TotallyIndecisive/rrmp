import { defineStore } from 'pinia'
import { player as playerApi } from '../services/api'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    currentTrack: null,
    isPlaying: false,
    positionMs: 0,
    durationMs: 0,
    volume: 100,
    queue: [],
    queueIndex: -1,
  }),

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
    },

    setQueue(queue, index = 0) {
      this.queue = queue
      this.queueIndex = index
    },

    async playTrack(track) {
      try {
        await playerApi.play(track.id)
        this.setTrack(track)
        this.setPlaying(true)
      } catch (error) {
        console.error('Failed to play track:', error)
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
        const response = await playerApi.next()
        if (response.data.track_id) {
          this.queueIndex = Math.min(this.queueIndex + 1, this.queue.length - 1)
        }
      } catch (error) {
        console.error('Failed to play next:', error)
      }
    },

    async previousTrack() {
      try {
        const response = await playerApi.previous()
        if (response.data.track_id) {
          this.queueIndex = Math.max(this.queueIndex - 1, 0)
        }
      } catch (error) {
        console.error('Failed to play previous:', error)
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
  },
})