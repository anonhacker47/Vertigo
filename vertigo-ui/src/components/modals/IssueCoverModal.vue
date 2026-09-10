<template>
  <div v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md transition-all duration-200">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl relative">
      <h3 class="text-lg font-bold text-white mb-1">Change Cover</h3>
      <p class="text-xs text-slate-400 mb-5">
        {{ hasOwnCover ? 'This issue has its own cover.' : 'This issue is showing the series cover.' }}
      </p>

      <div class="flex flex-col sm:flex-row gap-5 mb-6">
        <div class="shrink-0 mx-auto sm:mx-0">
          <div class="relative w-32 h-44 rounded-xl border border-slate-800 bg-slate-950 overflow-hidden">
            <img v-if="previewSrc && !previewFailed" :src="previewSrc" alt="Cover preview"
              class="w-full h-full object-cover" :class="{ 'opacity-40': !hasSelection }"
              @error="previewFailed = true" />
            <div v-else class="w-full h-full flex items-center justify-center p-2 text-center">
              <span class="text-xs text-slate-500">{{ previewFailed ? 'Preview unavailable' : 'No cover' }}</span>
            </div>
            <span
              class="absolute bottom-1 left-1 right-1 text-center text-[10px] font-bold uppercase tracking-wider text-slate-200 bg-slate-950/80 rounded-md px-1 py-0.5">
              {{ hasSelection ? 'New cover' : (hasOwnCover ? 'Current cover' : 'Series cover') }}
            </span>
          </div>
        </div>

        <div class="flex flex-col gap-4 flex-1 min-w-0">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Upload Image</label>
            <input ref="fileInputRef" type="file" accept="image/*" @change="onFileChange"
              class="block w-full text-sm text-slate-300 rounded-xl border border-slate-800 bg-slate-950 file:mr-3 file:rounded-l-xl file:border-0 file:bg-slate-800 file:px-3 file:py-2.5 file:text-xs file:font-semibold file:text-white file:cursor-pointer hover:file:bg-slate-700 focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>

          <div class="flex items-center gap-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
            <span class="flex-1 border-t border-slate-800"></span>
            or
            <span class="flex-1 border-t border-slate-800"></span>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Image URL</label>
            <input type="url" :value="localUrl" placeholder="https://" @input="onUrlInput" @keyup.enter="handleSave"
              class="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-4 text-white placeholder-slate-600 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary text-sm" />
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 justify-end border-t border-slate-800/60 pt-4">
        <button v-if="hasOwnCover" type="button" :disabled="busy" @click="$emit('remove')"
          class="mr-auto px-4 py-2 text-sm font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition disabled:opacity-50">
          Remove cover
        </button>
        <button type="button" :disabled="busy" @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition disabled:opacity-50">
          Cancel
        </button>
        <button type="button" :disabled="busy || !hasSelection" @click="handleSave"
          class="px-5 py-2 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition shadow-lg shadow-emerald-500/10 disabled:opacity-50 disabled:cursor-not-allowed">
          {{ busy ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue';

const props = defineProps<{
  show: boolean;
  /** Image currently shown for the issue (own cover or series fallback); used as the preview when nothing is picked. */
  currentImage?: string | null;
  hasOwnCover: boolean;
  /** True while the parent is saving/removing; disables the buttons. */
  busy?: boolean;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'save', source: File | string): void;
  (e: 'remove'): void;
}>();

const localFile = ref<File | null>(null);
const localUrl = ref('');
const fileObjectUrl = ref<string | null>(null);
const previewFailed = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const hasSelection = computed(() => !!localFile.value || localUrl.value.trim() !== '');

const previewSrc = computed(() => {
  if (localFile.value && fileObjectUrl.value) return fileObjectUrl.value;
  if (localUrl.value.trim()) return localUrl.value.trim();
  return props.currentImage || null;
});

function revokeObjectUrl() {
  if (fileObjectUrl.value) {
    URL.revokeObjectURL(fileObjectUrl.value);
    fileObjectUrl.value = null;
  }
}

function reset() {
  revokeObjectUrl();
  localFile.value = null;
  localUrl.value = '';
  previewFailed.value = false;
  if (fileInputRef.value) fileInputRef.value.value = '';
}

watch(() => props.show, (isShowing) => {
  if (isShowing) reset();
  else revokeObjectUrl();
});

watch(previewSrc, () => {
  previewFailed.value = false;
});

function onFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0] ?? null;
  revokeObjectUrl();
  localFile.value = file;
  if (file) {
    // A picked file replaces any URL typed earlier.
    localUrl.value = '';
    fileObjectUrl.value = URL.createObjectURL(file);
  }
}

function onUrlInput(event: Event) {
  localUrl.value = (event.target as HTMLInputElement).value;
  if (localUrl.value.trim() && localFile.value) {
    // A typed URL replaces any picked file.
    revokeObjectUrl();
    localFile.value = null;
    if (fileInputRef.value) fileInputRef.value.value = '';
  }
}

function handleSave() {
  if (props.busy) return;
  if (localFile.value) {
    emit('save', localFile.value);
    return;
  }
  const url = localUrl.value.trim();
  if (url) emit('save', url);
}

onBeforeUnmount(revokeObjectUrl);
</script>
