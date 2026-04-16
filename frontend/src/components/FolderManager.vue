<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-retro-cream rounded-lg w-full max-w-md mx-4">
      <div class="p-4 border-b border-retro-brown flex items-center justify-between">
        <h3 class="font-retro text-lg font-bold text-retro-brown">Manage Folders</h3>
        <button @click="close" class="btn-icon text-retro-warm hover:text-retro-brown">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-4">
        <div class="flex gap-2 mb-4">
          <input
            v-model="newFolderPath"
            type="text"
            placeholder="Enter folder path..."
            class="input-retro flex-1"
            @keyup.enter="addFolder"
          />
          <button @click="addFolder" class="btn-retro">Add</button>
        </div>

        <div v-if="scanning" class="text-center py-4 text-retro-warm font-retro">
          Scanning library...
        </div>
        <div v-else-if="scanResult" class="mb-4 p-3 bg-retro-brown bg-opacity-10 rounded">
          <p class="font-retro text-sm text-retro-brown">
            Scanned: {{ scanResult.scanned }} tracks
          </p>
          <p class="font-retro text-sm text-retro-warm">
            Skipped: {{ scanResult.skipped }} tracks
          </p>
        </div>

        <button @click="scanLibrary" class="btn-retro w-full mb-4">
          Scan Library
        </button>

        <div class="space-y-2 max-h-60 overflow-y-auto scrollbar-retro">
          <div v-if="folders.length === 0" class="text-center py-4 text-retro-warm font-retro text-sm">
            No folders added yet
          </div>
          <div
            v-for="folder in folders"
            :key="folder.id"
            class="folder-item p-3 bg-retro-brown bg-opacity-10 rounded flex items-center justify-between"
          >
            <span class="font-retro text-sm text-retro-brown truncate flex-1">{{ folder.path }}</span>
            <button
              @click="deleteFolder(folder.id)"
              class="btn-icon text-retro-warm hover:text-red-500"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLibraryStore } from '../stores/library'
import { library as libraryApi } from '../services/api'

const emit = defineEmits(['close', 'scan-complete'])

const libraryStore = useLibraryStore()

const folders = ref([])
const newFolderPath = ref('')
const scanning = ref(false)
const scanResult = ref(null)

onMounted(async () => {
  await fetchFolders()
})

async function fetchFolders() {
  try {
    const response = await libraryApi.getFolders()
    folders.value = response.data
  } catch (error) {
    console.error('Failed to fetch folders:', error)
  }
}

async function addFolder() {
  if (!newFolderPath.value.trim()) return
  try {
    const response = await libraryApi.addFolder({ path: newFolderPath.value.trim() })
    folders.value.push(response.data)
    newFolderPath.value = ''
  } catch (error) {
    console.error('Failed to add folder:', error)
    alert('Failed to add folder: ' + (error.response?.data?.detail || 'Unknown error'))
  }
}

async function deleteFolder(id) {
  try {
    await libraryApi.deleteFolder(id)
    folders.value = folders.value.filter(f => f.id !== id)
  } catch (error) {
    console.error('Failed to delete folder:', error)
  }
}

async function scanLibrary() {
  scanning.value = true
  scanResult.value = null
  try {
    const response = await libraryApi.scanLibrary()
    scanResult.value = response.data
    emit('scan-complete')
  } catch (error) {
    console.error('Failed to scan library:', error)
  } finally {
    scanning.value = false
  }
}

function close() {
  emit('close')
}
</script>