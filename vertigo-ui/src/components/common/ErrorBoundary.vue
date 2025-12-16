<template>
  <!-- Only show modal when error exists -->
  <Transition name="fade">
    <div v-if="error" class="fixed inset-0 z-50 flex items-center justify-center bg-transparent">
      
      <div class="modal-container">
        <h2 class="title">Something went wrong</h2>
        <p class="message">{{ error.message }}</p>

        <div class="actions">
          <button class="btn" @click="reload">Reload</button>
          <button class="btn-secondary" @click="dismiss">Dismiss</button>
        </div>
      </div>

    </div>
  </Transition>

  <!-- Content -->
  <slot v-if="!error" />
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'ErrorBoundaryModal',

  setup() {
    const error = ref<Error | null>(null)
    return { error }
  },

  errorCaptured(err) {
    (this as any).error = err
    console.error('[ErrorBoundary]', err)
    return false
  },

  methods: {
    reload() {
      window.location.reload()
    },
    dismiss() {
      this.error = null
    }
  }
})
</script>

<style scoped>
.modal-container {
  width: 90%;
  max-width: 420px;
  background: #1f2937;
  color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 0 25px rgba(0,0,0,0.4);
  text-align: center;
}

.title {
  font-size: 1.4rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.message {
  margin-bottom: 20px;
  opacity: 0.8;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn {
  background: #3b82f6;
  padding: 8px 18px;
  border-radius: 6px;
  font-weight: 500;
}

.btn-secondary {
  background: #6b7280;
  padding: 8px 18px;
  border-radius: 6px;
  font-weight: 500;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
