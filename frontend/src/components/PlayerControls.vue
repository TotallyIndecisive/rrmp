<template>
  <div class="player-controls border-t-2 border-retro-amber px-6 py-4" :class="isDark ? 'bg-retro-dark' : 'bg-retro-warm'">
    <div class="max-w-6xl mx-auto">
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <button @click="previous" class="btn-icon hover:text-retro-amber" :class="isDark ? 'text-retro-warm' : 'text-retro-cream'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>
          <button @click="togglePlay" class="btn-icon hover:text-retro-cream" :class="isDark ? 'text-retro-amber' : 'text-retro-amber'">
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>
          <button @click="stop" class="btn-icon hover:text-retro-amber" :class="isDark ? 'text-retro-warm' : 'text-retro-cream'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h12v12H6z"/>
            </svg>
          </button>
          <button @click="next" class="btn-icon hover:text-retro-amber" :class="isDark ? 'text-retro-warm' : 'text-retro-cream'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>
        </div>

        <div class="flex items-center gap-1 h-8" :class="{ 'vu-meter': isPlaying }">
          <div v-for="i in 5" :key="i" class="vu-bar w-1 rounded-full" :style="{ animationDelay: `${i * 0.1}s` }"></div>
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

        <div class="flex items-center gap-2">
          <button @click="toggleShuffle" class="btn-icon text-retro-warm hover:text-retro-amber" :class="{ 'text-retro-amber': shuffle }">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
            </svg>
          </button>
          <button @click="cycleRepeat" class="btn-icon text-retro-warm hover:text-retro-amber" :class="{ 'text-retro-amber': repeat !== 'off' }">
            <svg v-if="repeat === 'off'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
            </svg>
            <svg v-else-if="repeat === 'one'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4zm4-2v-3h-3V9h3V6h2v3h3v2h-3v3h-2z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
            </svg>
          </button>
          <button @click="toggleQueue" class="btn-icon text-retro-warm hover:text-retro-amber relative" :class="{ 'text-retro-amber': showQueue }">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            <span v-if="queueActive" class="absolute -top-1 -right-1 w-2 h-2 bg-retro-amber rounded-full"></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlayerStore } from '../stores/player'
import { useThemeStore } from '../stores/theme'

const playerStore = usePlayerStore()
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const positionMs = ref(0)
const durationMs = ref(0)
const isPlaying = ref(false)
const volume = ref(100)
const shuffle = ref(false)
const repeat = ref('off')
const showQueue = ref(false)
const queueActive = ref(false)

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
  shuffle.value = playerStore.shuffle
  repeat.value = playerStore.repeat
  showQueue.value = playerStore.showQueue
  queueActive.value = playerStore.queueActive

  pollInterval = setInterval(async () => {
    await playerStore.fetchStatus()
    positionMs.value = playerStore.positionMs
    durationMs.value = playerStore.durationMs
    isPlaying.value = playerStore.isPlaying
    volume.value = playerStore.volume
    shuffle.value = playerStore.shuffle
    repeat.value = playerStore.repeat
    showQueue.value = playerStore.showQueue
    queueActive.value = playerStore.queueActive
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

function toggleShuffle() {
  playerStore.toggleShuffle()
}

function cycleRepeat() {
  playerStore.cycleRepeat()
}

function toggleQueue() {
  playerStore.toggleQueue()
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

.vu-meter .vu-bar {
  background: linear-gradient(to top, #F5A623 0%, #8D6E63 100%);
  height: 100%;
  animation: vu-bounce 0.5s ease-in-out infinite alternate;
}

@keyframes vu-bounce {
  0% { transform: scaleY(0.3); }
  100% { transform: scaleY(1); }
}

@media (prefers-reduced-motion: reduce) {
  .vu-meter .vu-bar {
    animation: none;
  }
}

.btn-icon {
  transition: transform 0.15s ease, text-shadow 0.15s ease;
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