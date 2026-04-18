<template>
  <div class="library bg-retro-cream h-full flex flex-col">
    <div class="p-4 border-b border-retro-brown">
      <div class="flex items-center gap-2 mb-3">
        <h2 class="font-retro text-lg font-bold text-retro-brown flex-1">Library</h2>
        <button @click="showFolderManager = true" class="btn-retro text-xs">
          Folders
        </button>
      </div>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search tracks..."
        class="input-retro w-full"
        @input="handleSearch"
      />
    </div>

    <div class="flex-1 overflow-y-auto scrollbar-retro p-2">
      <div v-if="loading" class="text-center py-8 text-retro-warm font-retro">
        Loading...
      </div>
      <div v-else-if="filteredTracks.length === 0" class="text-center py-8 text-retro-warm font-retro">
        No tracks found
      </div>
      <div v-else class="space-y-1">
        <div
          v-for="track in filteredTracks"
          :key="track.id"
          class="track-item p-3 rounded cursor-pointer group"
          :class="{ 'bg-retro-amber': isCurrentTrack(track) }"
          @click="playTrack(track)"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="font-retro text-sm truncate" :class="isCurrentTrack(track) ? 'text-retro-dark' : 'text-retro-brown'">
                {{ track.title }}
              </p>
              <p class="font-retro text-xs truncate" :class="isCurrentTrack(track) ? 'text-retro-dark opacity-75' : 'text-retro-warm'">
                {{ track.artist || 'Unknown Artist' }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span class="font-retro text-xs" :class="isCurrentTrack(track) ? 'text-retro-dark' : 'text-retro-warm'">
                {{ formatDuration(track.duration) }}
              </span>
              <button
                @click.stop="showAddToPlaylist(track)"
                class="btn-icon opacity-0 group-hover:opacity-100 text-retro-brown hover:text-retro-amber"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button
                @click.stop="addToQueue(track)"
                class="btn-icon opacity-0 group-hover:opacity-100 text-retro-brown hover:text-retro-amber"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <FolderManager 
      v-if="showFolderManager" 
      @close="showFolderManager = false"
      @scan-complete="refreshTracks"
    />

    <div v-if="showPlaylistModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-retro-cream rounded-lg p-4 w-80">
        <h3 class="font-retro text-lg font-bold text-retro-brown mb-4">Add to Playlist</h3>
        <div v-if="playlists.length === 0" class="text-center py-4 text-retro-warm font-retro text-sm">
          No playlists yet
        </div>
        <div v-else class="space-y-2">
          <button
            v-for="playlist in playlists"
            :key="playlist.id"
            @click="addToPlaylist(playlist.id)"
            class="w-full text-left p-2 rounded font-retro text-sm text-retro-brown hover:bg-retro-amber hover:text-retro-dark"
          >
            {{ playlist.name }}
          </button>
        </div>
        <button @click="showPlaylistModal = false" class="mt-4 btn-retro w-full text-xs">
          Cancel
        </button>
      </div>
    </div>

    <div class="border-t border-retro-brown">
      <button
        @click="toggleRecent"
        class="w-full p-3 flex items-center justify-between hover:bg-retro-amber hover:bg-opacity-20 transition-colors"
      >
        <h3 class="font-retro text-sm font-bold text-retro-brown">Recently Played</h3>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 text-retro-warm transition-transform"
          :class="{ 'rotate-180': showRecent }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <div v-if="showRecent" class="max-h-60 overflow-y-auto scrollbar-retro p-2 border-t border-retro-brown">
        <div v-if="recentLoading" class="text-center py-4 text-retro-warm font-retro text-xs">
          Loading...
        </div>
        <div v-else-if="recentTracks.length === 0" class="text-center py-4 text-retro-warm font-retro text-xs">
          No recent tracks
        </div>
        <div v-else class="space-y-1">
          <div
            v-for="track in recentTracks"
            :key="track.id"
            class="track-item p-2 rounded cursor-pointer group"
            :class="{ 'bg-retro-amber': isCurrentTrack(track) }"
            @click="playTrack(track)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="font-retro text-xs truncate" :class="isCurrentTrack(track) ? 'text-retro-dark' : 'text-retro-brown'">
                  {{ track.title }}
                </p>
                <p class="font-retro text-xs truncate" :class="isCurrentTrack(track) ? 'text-retro-dark opacity-75' : 'text-retro-warm'">
                  {{ track.artist || 'Unknown Artist' }}
                </p>
              </div>
              <span class="font-retro text-xs" :class="isCurrentTrack(track) ? 'text-retro-dark' : 'text-retro-warm'">
                {{ formatDuration(track.duration) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLibraryStore } from '../stores/library'
import { usePlayerStore } from '../stores/player'
import { playlists as playlistsApi, library } from '../services/api'
import { toast } from '../utils/toast'
import FolderManager from './FolderManager.vue'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()

const searchQuery = ref('')
const loading = ref(false)
const showFolderManager = ref(false)
const showPlaylistModal = ref(false)
const selectedTrack = ref(null)
const playlists = ref([])
const showRecent = ref(false)
const recentTracks = ref([])
const recentLoading = ref(false)

const filteredTracks = computed(() => {
  if (!searchQuery.value) return libraryStore.tracks
  const query = searchQuery.value.toLowerCase()
  return libraryStore.tracks.filter(track =>
    track.title?.toLowerCase().includes(query) ||
    track.artist?.toLowerCase().includes(query) ||
    track.album?.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  await refreshTracks()
  await fetchPlaylists()
})

async function refreshTracks() {
  loading.value = true
  try {
    await libraryStore.fetchTracks()
  } finally {
    loading.value = false
  }
}

async function fetchPlaylists() {
  try {
    const response = await playlistsApi.getAll()
    playlists.value = response.data
  } catch (error) {
    console.error('Failed to fetch playlists:', error)
  }
}

function handleSearch() {
  libraryStore.setSearch(searchQuery.value)
}

function isCurrentTrack(track) {
  return playerStore.currentTrack?.id === track.id
}

async function playTrack(track) {
  console.log('Library.vue: Clicked track_id:', track.id)
  console.log('Library.vue: Calling playerApi.play with track_id:', track.id)
  await playerStore.playTrack(track)
  console.log('Library.vue: Player store updated, currentTrack:', playerStore.currentTrack)
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function showAddToPlaylist(track) {
  selectedTrack.value = track
  showPlaylistModal.value = true
}

async function addToPlaylist(playlistId) {
  if (!selectedTrack.value) return
  console.log('Library.vue: Adding track_id:', selectedTrack.value.id, 'to playlist_id:', playlistId)
  try {
    const response = await playlistsApi.addTrack(playlistId, selectedTrack.value.id)
    console.log('Library.vue: Add track response:', response.data)
    showPlaylistModal.value = false
    selectedTrack.value = null
  } catch (error) {
    console.error('Library.vue: Failed to add track to playlist:', error)
  }
}

function addToQueue(track) {
  const result = playerStore.addToQueue(track)
  if (result.duplicate) {
    toast(`${result.title} is already in the queue`, 'info', 2000)
  } else {
    toast(`Added to queue: ${result.title}`, 'success', 2000)
  }
}

async function toggleRecent() {
  showRecent.value = !showRecent.value
  if (showRecent.value && recentTracks.value.length === 0) {
    recentLoading.value = true
    try {
      const response = await library.getRecent()
      recentTracks.value = response.data
    } catch (error) {
      console.error('Failed to fetch recent tracks:', error)
    } finally {
      recentLoading.value = false
    }
  }
}
</script>

<style scoped>
.track-item:hover {
  background-color: rgba(245, 166, 35, 0.2);
}
</style>