<template>
  <div class="flex flex-col items-center justify-center h-full p-8">
    <div v-if="track" class="cassette">
      <div class="cassette-body">
        <div class="cassette-label">
          <div v-if="albumArt" class="album-art">
            <img :src="`data:image/jpeg;base64,${albumArt}`" alt="Album Art" />
          </div>
          <div v-else class="cassette-stripe"></div>
        </div>
        <div class="cassette-reels">
          <div class="reel left" :class="{ spinning: isPlaying }">
            <div class="reel-hole"></div>
            <div class="reel-spoke"></div>
            <div class="reel-spoke" style="transform: rotate(60deg)"></div>
            <div class="reel-spoke" style="transform: rotate(120deg)"></div>
          </div>
          <div class="reel right" :class="{ spinning: isPlaying }">
            <div class="reel-hole"></div>
            <div class="reel-spoke"></div>
            <div class="reel-spoke" style="transform: rotate(60deg)"></div>
            <div class="reel-spoke" style="transform: rotate(120deg)"></div>
          </div>
        </div>
      </div>
      <div class="cassette-screw top-left"></div>
      <div class="cassette-screw top-right"></div>
      <div class="cassette-screw bottom-left"></div>
      <div class="cassette-screw bottom-right"></div>
    </div>
    <div v-else class="font-retro text-lg" :class="isDark ? 'text-retro-warm' : 'text-retro-warm'">
      No track playing
    </div>
    <div v-if="track" class="mt-6 text-center">
      <h2 class="font-retro text-xl font-bold" :class="isDark ? 'text-retro-cream' : 'text-retro-brown'">{{ track.title }}</h2>
      <p class="font-retro text-sm mt-1" :class="isDark ? 'text-retro-warm' : 'text-retro-dark'">{{ track.artist || 'Unknown Artist' }}</p>
      <p class="font-retro text-xs mt-1" :class="isDark ? 'text-retro-warm' : 'text-retro-dark'">{{ track.album || 'Unknown Album' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { usePlayerStore } from '../stores/player'
import { useThemeStore } from '../stores/theme'
import { metadata } from '../services/api'

const playerStore = usePlayerStore()
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
const albumArt = ref(null)

const track = ref(null)
const isPlaying = ref(false)

watch(() => playerStore.currentTrack, async (newTrack) => {
  track.value = newTrack
  if (newTrack) {
    await fetchAlbumArt(newTrack.id)
  } else {
    albumArt.value = null
  }
}, { immediate: true })

watch(() => playerStore.isPlaying, (playing) => {
  isPlaying.value = playing
}, { immediate: true })

async function fetchAlbumArt(trackId) {
  try {
    const response = await metadata.getMetadata(trackId)
    albumArt.value = response.data.album_art
  } catch (error) {
    console.error('Failed to fetch album art:', error)
    albumArt.value = null
  }
}

onMounted(() => {
  track.value = playerStore.currentTrack
  isPlaying.value = playerStore.isPlaying
})
</script>

<style scoped>
.cassette {
  position: relative;
  width: 280px;
}

.cassette-body {
  background: linear-gradient(180deg, #4a3228 0%, #3E2723 100%);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 2px solid #5d4037;
}

.cassette-label {
  background: #F5F0E8;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.album-art {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
}

.album-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cassette-stripe {
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #F5A623 0%, #8D6E63 50%, #F5A623 100%);
  border-radius: 2px;
}

.cassette-reels {
  display: flex;
  justify-content: space-around;
  padding: 8px 20px;
}

.reel {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #1C1009 0%, #3E2723 100%);
  border-radius: 50%;
  border: 3px solid #8D6E63;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reel-hole {
  width: 20px;
  height: 20px;
  background: #F5A623;
  border-radius: 50%;
  border: 2px solid #8D6E63;
}

.reel-spoke {
  position: absolute;
  width: 50px;
  height: 3px;
  background: #5d4037;
  transform-origin: center;
}

.reel.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.cassette-screw {
  position: absolute;
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #9e9e9e 0%, #616161 100%);
  border-radius: 50%;
  border: 1px solid #424242;
}

.cassette-screw::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 2px;
  background: #424242;
}

.cassette-screw.top-left { top: 8px; left: 8px; }
.cassette-screw.top-right { top: 8px; right: 8px; }
.cassette-screw.bottom-left { bottom: 8px; left: 8px; }
.cassette-screw.bottom-right { bottom: 8px; right: 8px; }
</style>