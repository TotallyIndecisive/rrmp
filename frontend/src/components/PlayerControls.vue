<template>
  <div class="player-controls bg-retro-dark border-t-2 border-retro-brown px-6 py-4">
    <div class="max-w-6xl mx-auto">
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <button @click="previous" class="btn-icon text-retro-warm hover:text-retro-amber">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>
          <button @click="togglePlay" class="btn-icon text-retro-amber hover:text-retro-cream">
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>
          <button @click="stop" class="btn-icon text-retro-warm hover:text-retro-amber">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h12v12H6z"/>
            </svg>
          </button>
          <button @click="next" class="btn-icon text-retro-warm hover:text-retro-amber">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>
        </div>

        <div class="flex-1">
          <div class="flex items-center gap-4">
            <span class="font-retro text-xs text-retro-warm w-12">{{ formatTime(positionMs) }}</span>
            <div class="flex-1 relative">
              <div class="seek-bar bg-retro-brown rounded-full h-2 cursor-pointer" @click="seek">
                <div 
                  class="seek-progress bg-retro-amber rounded-full h-full transition-all"
                  :style="{ width: `${progress}%` }"
                ></div>
              </div>
            </div>
            <span class="font-retro text-xs text-retro-warm w-12">{{ formatTime(durationMs) }}</span>
          </div>
        </div>

        <div class="flex items-center gap-2 w-32">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-retro-warm" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
          </svg>
          <input 
            type="range" 
            min="0" 
            max="100" 
            :value="volume" 
            @input="setVolume"
            class="volume-slider w-full accent-retro-amber"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const positionMs = ref(0)
const durationMs = ref(0)
const isPlaying = ref(false)
const volume = ref(100)

let pollInterval = null

const progress = computed(() => {
  if (durationMs.value === 0) return 0
  return (positionMs.value / durationMs.value) * 100
})

onMounted(() => {
  positionMs.value = playerStore.positionMs
  durationMs.value = playerStore.durationMs
  isPlaying.value = playerStore.isPlaying
  volume.value = playerStore.volume

  pollInterval = setInterval(async () => {
    await playerStore.fetchStatus()
    positionMs.value = playerStore.positionMs
    durationMs.value = playerStore.durationMs
    isPlaying.value = playerStore.isPlaying
    volume.value = playerStore.volume
  }, 1000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

function formatTime(ms) {
  const totalSeconds = Math.floor(ms / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

function togglePlay() {
  if (isPlaying.value) {
    playerStore.pause()
  } else {
    playerStore.resume()
  }
}

function stop() {
  playerStore.stop()
}

function next() {
  playerStore.nextTrack()
}

function previous() {
  playerStore.previousTrack()
}

function seek(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const newPosition = Math.floor(percent * durationMs.value)
  playerStore.seek(newPosition)
}

function setVolume(event) {
  playerStore.setVolume(parseInt(event.target.value))
}
</script>

<style scoped>
.seek-bar {
  position: relative;
}

.seek-bar:hover .seek-progress {
  box-shadow: 0 0 8px rgba(245, 166, 35, 0.5);
}

.volume-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  background: #3E2723;
  border-radius: 2px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: #F5A623;
  border-radius: 50%;
  cursor: pointer;
}

.volume-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #F5A623;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}
</style>