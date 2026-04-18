<template>
  <div class="app-container bg-retro-dark min-h-screen flex flex-col" :class="{ 'mini-mode': isMiniMode }">
    <header class="bg-retro-brown px-4 py-2 border-b-2 border-retro-amber flex items-center justify-between">
      <h1 class="font-retro text-lg text-retro-cream font-bold tracking-wider">RETRO REEL MP</h1>
      <button @click="toggleMiniMode" class="btn-retro text-xs flex items-center gap-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        {{ isMiniMode ? 'Full' : 'Mini' }}
      </button>
    </header>
    
    <main class="flex-1 flex overflow-hidden">
      <aside v-if="!isMiniMode" class="w-72 flex-shrink-0 border-r-2 border-retro-brown">
        <Library />
      </aside>
      
      <section class="flex-1 flex items-center justify-center bg-retro-dark" :class="{ 'py-2': isMiniMode }">
        <NowPlaying :class="{ 'scale-50': isMiniMode }" />
      </section>
      
      <aside v-if="!isMiniMode" class="w-72 flex-shrink-0 border-l-2 border-retro-brown">
        <Playlist />
      </aside>
    </main>
    
    <PlayerControls :class="{ 'py-2': isMiniMode }" />
    <Queue />
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useLibraryStore } from './stores/library'
import { usePlayerStore } from './stores/player'
import { toast } from './utils/toast'
import { windowApi } from './services/api'
import Library from './components/Library.vue'
import NowPlaying from './components/NowPlaying.vue'
import Playlist from './components/Playlist.vue'
import PlayerControls from './components/PlayerControls.vue'
import Queue from './components/Queue.vue'
import Toast from './components/Toast.vue'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toastRef = ref(null)
const isMiniMode = ref(false)

let previousVolume = 100

const MINI_WIDTH = 480
const MINI_HEIGHT = 200
const FULL_WIDTH = 1280
const FULL_HEIGHT = 800

async function toggleMiniMode() {
  isMiniMode.value = !isMiniMode.value
  if (isMiniMode.value) {
    await windowApi.resize(MINI_WIDTH, MINI_HEIGHT)
    toast('Mini mode', 'info', 1500)
  } else {
    await windowApi.resize(FULL_WIDTH, FULL_HEIGHT)
    toast('Full mode', 'info', 1500)
  }
}

function handleKeydown(event) {
  const key = event.key

  if (key === ' ') {
    event.preventDefault()
    togglePlayPause()
    return
  }

  if (key === 'ArrowRight') {
    event.preventDefault()
    seekForward()
    return
  }

  if (key === 'ArrowLeft') {
    event.preventDefault()
    seekBackward()
    return
  }

  if (key === 'ArrowUp') {
    event.preventDefault()
    adjustVolume(10)
    return
  }

  if (key === 'ArrowDown') {
    event.preventDefault()
    adjustVolume(-10)
    return
  }

  if (key === 'n' || key === 'N') {
    event.preventDefault()
    nextTrack()
    return
  }

  if (key === 'p' || key === 'P') {
    event.preventDefault()
    previousTrack()
    return
  }

  if (key === 's' || key === 'S') {
    event.preventDefault()
    toggleShuffle()
    return
  }

  if (key === 'r' || key === 'R') {
    event.preventDefault()
    cycleRepeat()
    return
  }

  if (key === 'm' || key === 'M') {
    event.preventDefault()
    toggleMute()
    return
  }
}

async function togglePlayPause() {
  if (playerStore.isPlaying) {
    await playerStore.pause()
    toast('Paused', 'info', 1500)
  } else {
    await playerStore.resume()
    toast('Playing', 'info', 1500)
  }
}

async function adjustVolume(delta) {
  const newVolume = Math.max(0, Math.min(100, playerStore.volume + delta))
  await playerStore.setVolume(newVolume)
  toast(delta > 0 ? `+${delta}%` : `${delta}%`, 'info', 1500)
}

async function nextTrack() {
  await playerStore.nextTrack()
  toast('Next', 'info', 1500)
}

async function previousTrack() {
  await playerStore.previousTrack()
  toast('Previous', 'info', 1500)
}

async function toggleShuffle() {
  await playerStore.toggleShuffle()
  toast(playerStore.shuffle ? 'Shuffle ON' : 'Shuffle OFF', 'info', 1500)
}

async function cycleRepeat() {
  await playerStore.cycleRepeat()
  let label = 'Off'
  if (playerStore.repeat === 'one') label = 'Repeat 1'
  else if (playerStore.repeat === 'all') label = 'Repeat All'
  toast(label, 'info', 1500)
}

async function toggleMute() {
  if (playerStore.volume > 0) {
    previousVolume = playerStore.volume
    await playerStore.setVolume(0)
    toast('Muted', 'info', 1500)
  } else {
    await playerStore.setVolume(previousVolume || 100)
    toast(`Volume ${previousVolume || 100}%`, 'info', 1500)
  }
}

async function seekForward() {
  const newPosition = playerStore.positionMs + 10000
  await playerStore.seek(newPosition)
  toast('+10s', 'info', 1500)
}

async function seekBackward() {
  const newPosition = Math.max(0, playerStore.positionMs - 10000)
  await playerStore.seek(newPosition)
  toast('-10s', 'info', 1500)
}

onMounted(async () => {
  await Promise.all([
    libraryStore.fetchTracks(),
    libraryStore.fetchFolders(),
    libraryStore.fetchPlaylists(),
    playerStore.fetchStatus(),
  ])
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.mini-mode .player-controls {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}

.mini-mode main {
  padding-bottom: 60px;
}
</style>