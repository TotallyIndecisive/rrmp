<template>
  <div class="app-container bg-retro-dark min-h-screen flex flex-col">
    <header class="bg-retro-brown px-6 py-3 border-b-2 border-retro-amber">
      <h1 class="font-retro text-xl text-retro-cream font-bold tracking-wider">RETRO REEL MP</h1>
    </header>
    
    <main class="flex-1 flex overflow-hidden">
      <aside class="w-72 flex-shrink-0 border-r-2 border-retro-brown">
        <Library />
      </aside>
      
      <section class="flex-1 flex items-center justify-center bg-retro-dark">
        <NowPlaying />
      </section>
      
      <aside class="w-72 flex-shrink-0 border-l-2 border-retro-brown">
        <Playlist />
      </aside>
    </main>
    
    <PlayerControls />
    <Queue />
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useLibraryStore } from './stores/library'
import { usePlayerStore } from './stores/player'
import { toast } from './utils/toast'
import Library from './components/Library.vue'
import NowPlaying from './components/NowPlaying.vue'
import Playlist from './components/Playlist.vue'
import PlayerControls from './components/PlayerControls.vue'
import Queue from './components/Queue.vue'
import Toast from './components/Toast.vue'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toastRef = ref(null)

let previousVolume = 100

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