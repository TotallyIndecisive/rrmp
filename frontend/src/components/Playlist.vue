<template>
  <div class="playlist-panel h-full flex flex-col" :class="isDark ? 'bg-retro-cream' : 'bg-white'" style="height: 100%; max-height: 100%; display: flex; flex-direction: column; overflow: hidden;">
    <div class="p-4 border-b" :class="isDark ? 'border-retro-brown' : 'border-retro-warm'" style="flex-shrink: 0;">
      <div class="flex items-center gap-2 mb-3">
        <h2 class="font-retro text-lg font-bold flex-1" :class="isDark ? 'text-retro-brown' : 'text-retro-dark'">Playlists</h2>
        <button @click="createNewPlaylist" class="btn-retro text-xs">
          New
        </button>
      </div>
      <input
        v-if="showNewPlaylistInput"
        v-model="newPlaylistName"
        type="text"
        placeholder="Playlist name"
        class="input-retro w-full mb-2"
        @keyup.enter="saveNewPlaylist"
        @keyup.escape="cancelNewPlaylist"
        ref="newPlaylistInput"
      />
    </div>

    <div class="flex-1 overflow-y-auto p-2" style="flex: 1; min-height: 0; overflow-y: auto;" data-scroll-area="playlist">
      <div v-if="loading" class="text-center py-8 text-retro-warm font-retro">
        Loading...
      </div>
      <div v-else-if="playlists.length === 0" class="text-center py-8 text-retro-warm font-retro">
        No playlists yet
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="playlist in playlists"
          :key="playlist.id"
          class="playlist-item rounded overflow-hidden"
        >
          <div
            class="p-3 cursor-pointer flex items-center justify-between hover:bg-retro-amber hover:bg-opacity-20"
            :class="{ 'bg-retro-amber bg-opacity-20': expandedPlaylist === playlist.id }"
            @click="togglePlaylist(playlist.id)"
          >
            <span class="font-retro text-sm text-retro-brown truncate">{{ playlist.name }}</span>
            <div class="flex items-center gap-2">
              <span v-if="playlist.trackCount > 0" class="font-retro text-xs text-retro-warm bg-retro-amber bg-opacity-20 px-2 py-0.5 rounded">
                {{ playlist.trackCount }}
              </span>
              <button
                @click.stop="playPlaylist(playlist.id)"
                class="btn-icon text-retro-amber hover:text-retro-brown"
                title="Play playlist"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                @click.stop="deletePlaylist(playlist.id)"
                class="btn-icon text-retro-warm hover:text-red-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-retro-warm transition-transform"
                :class="{ 'rotate-180': expandedPlaylist === playlist.id }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div v-if="expandedPlaylist === playlist.id" class="playlist-tracks p-2 bg-retro-brown bg-opacity-10" style="display: block; overflow: visible;">
            <div v-if="loadingPlaylist" class="text-center py-4 text-retro-warm font-retro text-xs">
              Loading...
            </div>
            <div v-else-if="!playlistTracks[playlist.id] || playlistTracks[playlist.id].length === 0" class="text-center py-4 text-retro-warm font-retro text-xs">
              No tracks in playlist
            </div>
            <draggable
              v-else
              :list="playlistTracks[playlist.id]"
              item-key="id"
              @end="(e) => reorderTracks(playlist.id, playlistTracks[playlist.id])"
              class="space-y-1"
            >
              <template #item="{ element }">
                <div
                  class="track-row p-2 rounded cursor-pointer hover:bg-retro-amber hover:bg-opacity-30 flex items-center gap-2"
                  @click="playTrack(element)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-retro-warm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="font-retro text-xs truncate text-retro-brown">{{ element.title }}</p>
                    <p class="font-retro text-xs truncate text-retro-warm">{{ element.artist }}</p>
                  </div>
                  <span class="font-retro text-xs text-retro-warm">
                    {{ formatDuration(element.duration) }}
                  </span>
                  <button
                    @click.stop="removeTrack(playlist.id, element.track_id)"
                    class="btn-icon text-retro-warm hover:text-red-500 p-1"
                    title="Remove track"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useLibraryStore } from '../stores/library'
import { usePlayerStore } from '../stores/player'
import { useThemeStore } from '../stores/theme'
import { playlists as playlistsApi } from '../services/api'
import { toast } from '../utils/toast'
import draggable from 'vuedraggable'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const playlists = ref([])
const playlistTracks = ref({})
const expandedPlaylist = ref(null)
const loading = ref(false)
const loadingPlaylist = ref(false)
const showNewPlaylistInput = ref(false)
const newPlaylistName = ref('')
const newPlaylistInput = ref(null)

onMounted(async () => {
  await fetchPlaylists()
})

async function fetchPlaylists() {
  loading.value = true
  try {
    const response = await playlistsApi.getAll()
    playlists.value = response.data.map(p => ({ ...p, trackCount: 0 }))
  } catch (error) {
    console.error('Failed to fetch playlists:', error)
  } finally {
    loading.value = false
  }
}

async function togglePlaylist(playlistId) {
  if (expandedPlaylist.value === playlistId) {
    expandedPlaylist.value = null
    return
  }
  expandedPlaylist.value = playlistId
  if (!playlistTracks.value[playlistId]) {
    await fetchPlaylistTracks(playlistId)
  }
  updatePlaylistCount(playlistId)
}

function updatePlaylistCount(playlistId) {
  const playlist = playlists.value.find(p => p.id === playlistId)
  if (playlist && playlistTracks.value[playlistId]) {
    playlist.trackCount = playlistTracks.value[playlistId].length
  }
}

async function fetchPlaylistTracks(playlistId) {
  console.log('Playlist.vue: Fetching tracks for playlist_id:', playlistId)
  loadingPlaylist.value = true
  try {
    const response = await playlistsApi.getOne(playlistId)
    console.log('Playlist.vue: Full response:', response.data)
    console.log('Playlist.vue: Got tracks:', response.data.tracks)
    playlistTracks.value[playlistId] = response.data.tracks
  } catch (error) {
    console.error('Playlist.vue: Failed to fetch playlist tracks:', error)
  } finally {
    loadingPlaylist.value = false
  }
}

function createNewPlaylist() {
  showNewPlaylistInput.value = true
  newPlaylistName.value = ''
  nextTick(() => {
    newPlaylistInput.value?.focus()
  })
}

async function saveNewPlaylist() {
  if (!newPlaylistName.value.trim()) return
  try {
    const response = await playlistsApi.create(newPlaylistName.value.trim())
    playlists.value.push(response.data)
    showNewPlaylistInput.value = false
    newPlaylistName.value = ''
  } catch (error) {
    console.error('Failed to create playlist:', error)
  }
}

function cancelNewPlaylist() {
  showNewPlaylistInput.value = false
  newPlaylistName.value = ''
}

async function deletePlaylist(playlistId) {
  try {
    await playlistsApi.remove(playlistId)
    playlists.value = playlists.value.filter(p => p.id !== playlistId)
    delete playlistTracks.value[playlistId]
    if (expandedPlaylist.value === playlistId) {
      expandedPlaylist.value = null
    }
    toast('Playlist deleted', 'success', 2000)
  } catch (error) {
    console.error('Failed to delete playlist:', error)
    toast('Failed to delete playlist', 'error', 3000)
  }
}

async function removeTrack(playlistId, trackId) {
  try {
    await playlistsApi.removeTrack(playlistId, trackId)
    if (playlistTracks.value[playlistId]) {
      playlistTracks.value[playlistId] = playlistTracks.value[playlistId].filter(t => t.track_id !== trackId)
      const playlist = playlists.value.find(p => p.id === playlistId)
      if (playlist) {
        playlist.trackCount = playlistTracks.value[playlistId].length
      }
    }
    toast('Removed from playlist', 'success', 2000)
  } catch (error) {
    console.error('Failed to remove track:', error)
    toast('Failed to remove track', 'error', 3000)
  }
}

async function reorderTracks(playlistId, newOrder) {
  const trackIds = newOrder.map(t => t.track_id)
  try {
    await playlistsApi.reorder(playlistId, trackIds)
    playlistTracks.value[playlistId] = newOrder
  } catch (error) {
    console.error('Failed to reorder tracks:', error)
    await fetchPlaylistTracks(playlistId)
  }
}

async function playTrack(track) {
  const fullTrack = {
    ...track,
    id: track.track_id,
    file_path: track.file_path
  }
  await playerStore.playTrack(fullTrack)
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function playPlaylist(playlistId) {
  try {
    console.log('Playlist.vue: playPlaylist called with playlist_id:', playlistId)
    const response = await playlistsApi.getOne(playlistId)
    console.log('Playlist.vue: Got playlist:', response.data)
    const tracks = response.data.tracks
    console.log('Playlist.vue: Playlist tracks:', tracks)
    if (tracks.length === 0) {
      toast('Playlist is empty', 'info', 2000)
      return
    }
    const queueTracks = tracks.map(track => ({
      id: track.track_id,
      title: track.title,
      artist: track.artist,
      album: track.album,
      duration: track.duration,
      file_path: track.file_path
    }))
    console.log('Playlist.vue: Setting queue with tracks:', queueTracks)
    playerStore.setQueue(queueTracks, 0)
    await playerStore.syncQueueToBackend()
    const firstTrack = queueTracks[0]
    console.log('Playlist.vue: Playing first track:', firstTrack)
    await playerStore.playTrack(firstTrack)
    toast(`Playing: ${response.data.name}`, 'success', 2000)
  } catch (error) {
    console.error('Failed to play playlist:', error)
    toast('Failed to play playlist', 'error', 3000)
  }
}
</script>

<style scoped>
.playlist-item:hover .btn-icon {
  opacity: 1;
}

.btn-icon {
  transition: transform 0.15s ease, text-shadow 0.15s ease, color 0.15s ease;
}

.btn-icon:hover {
  transform: scale(1.1);
  text-shadow: 0 0 8px #F5A623;
}

.btn-retro {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn-retro:hover {
  transform: scale(1.05);
  box-shadow: 0 0 12px rgba(245, 166, 35, 0.4);
}

@media (prefers-reduced-motion: reduce) {
  .btn-icon,
  .btn-retro {
    transition: none;
  }
}
</style>