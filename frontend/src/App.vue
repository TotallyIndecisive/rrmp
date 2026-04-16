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
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLibraryStore } from './stores/library'
import { usePlayerStore } from './stores/player'
import Library from './components/Library.vue'
import NowPlaying from './components/NowPlaying.vue'
import Playlist from './components/Playlist.vue'
import PlayerControls from './components/PlayerControls.vue'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()

onMounted(async () => {
  await Promise.all([
    libraryStore.fetchTracks(),
    libraryStore.fetchFolders(),
    libraryStore.fetchPlaylists(),
    playerStore.fetchStatus(),
  ])
})
</script>