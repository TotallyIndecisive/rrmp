import { reactive } from 'vue'

const state = reactive({
  toasts: [],
  idCounter: 0
})

let toastRef = null

export function setToastRef(component) {
  toastRef = component
}

export function showToast(message, type = 'info', duration = 3000) {
  if (toastRef) {
    toastRef.showToast(message, type, duration)
  }
}

export function toast(message, type = 'info', duration = 3000) {
  showToast(message, type, duration)
}

export function toastError(message) {
  showToast(message, 'error', 4000)
}

export function toastSuccess(message) {
  showToast(message, 'success', 3000)
}