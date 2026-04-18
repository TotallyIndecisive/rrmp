<template>
  <Transition name="slide">
    <div v-if="showQueue" class="fixed inset-0 z-50 flex justify-end" @click.self="closeQueue">
      <div class="w-80 bg-retro-cream h-full border-l-2 border-retro-brown shadow-lg flex flex-col">
        <div class="p-4 border-b border-retro-brown flex items-center justify-between">
          <h2 class="font-retro text-lg font-bold text-retro-brown">Queue</h2>
          <div class="flex items-center gap-2">
            <button
              v-if="playerStore.queue.length > 0"
              @click="clearQueue"
              class="btn-retro text-xs"
            >
              Clear
            </button>
            <button @click="closeQueue" class="btn-icon text-retro-warm hover:text-retro-amber">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto scrollbar-retro p-2">
          <div v-if="playerStore.queue.length === 0" class="text-center py-8 text-retro-warm font-retro text-sm">
            Queue is empty
          </div>
          <div v-else>
            <div
              v-for="(track, index) in playerStore.queue"
              :key="track.id"
              class="track-item p-2 rounded mb-1 group"
              :class="{ 
                'bg-retro-amber': index === playerStore.queueIndex,
                'opacity-40': index < playerStore.queueIndex
              }"
            >
              <div class="flex items-center gap-2">
                <span
                  class="font-retro text-xs w-6"
                  :class="index === playerStore.queueIndex ? 'text-retro-dark' : 'text-retro-warm'"
                >
                  {{ index + 1 }}
                </span>
                <div
                  class="flex-1 min-w-0 cursor-pointer"
                  @click="playFromQueue(index)"
                >
                  <p class="font-retro text-sm truncate" :class="index === playerStore.queueIndex ? 'text-retro-dark' : 'text-retro-brown'">
                    {{ track.title }}
                  </p>
                  <p class="font-retro text-xs truncate" :class="index === playerStore.queueIndex ? 'text-retro-dark opacity-75' : 'text-retro-warm'">
                    {{ track.artist || 'Unknown Artist' }}
                  </p>
                </div>
                <button
                  @click="removeFromQueue(index)"
                  class="btn-icon opacity-0 group-hover:opacity-100 text-retro-warm hover:text-red-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div v-if="!playerStore.queueActive && playerStore.queue.length > 0" class="mt-3 pt-3 border-t border-retro-brown">
              <p class="font-retro text-xs text-retro-warm text-center">
                Queue finished — continuing from library
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const showQueue = computed(() => playerStore.showQueue)

function closeQueue() {
  playerStore.setShowQueue(false)
}

function clearQueue() {
  playerStore.clearQueue()
  playerStore.setShowQueue(false)
}

function removeFromQueue(index) {
  playerStore.removeFromQueue(index)
}

function playFromQueue(index) {
  playerStore.playFromQueue(index)
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}

.track-item:hover {
  background-color: rgba(245, 166, 35, 0.2);
}
</style>