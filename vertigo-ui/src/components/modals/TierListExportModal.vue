<template>
  <div v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md transition-all duration-200">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl relative">
      <h3 class="text-lg font-bold text-white mb-5">Download Tier List</h3>

      <div class="flex flex-col gap-4 mb-6">
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider" for="tier-export-title">Title</label>
          <input id="tier-export-title" ref="inputRef" v-model="localTitle" type="text" maxlength="120"
            class="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-4 text-white placeholder-slate-600 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary text-sm"
            placeholder="My Tier List" :disabled="busy" @keyup.enter="handleConfirm" />
        </div>
      </div>

      <div class="flex items-center gap-3 justify-end border-t border-slate-800/60 pt-4">
        <button :disabled="busy" @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition disabled:opacity-50">
          Cancel
        </button>
        <button :disabled="busy || !localTitle.trim()" @click="handleConfirm"
          class="px-5 py-2 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition shadow-lg shadow-emerald-500/10 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
          <span v-if="busy" class="loading loading-spinner loading-xs"></span>
          {{ busy ? 'Rendering…' : 'Download' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onBeforeUnmount } from 'vue';

const props = defineProps<{
  show: boolean;
  initialTitle: string;
  busy: boolean;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'confirm', payload: { title: string }): void;
}>();

const localTitle = ref('');
const inputRef = ref<HTMLInputElement | null>(null);

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && !props.busy) emit('cancel');
}

watch(() => props.show, (isShowing) => {
  if (isShowing) {
    localTitle.value = props.initialTitle;
    window.addEventListener('keydown', onKeydown);
    nextTick(() => {
      inputRef.value?.focus();
      inputRef.value?.select();
    });
  } else {
    window.removeEventListener('keydown', onKeydown);
  }
});

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));

function handleConfirm() {
  const title = localTitle.value.trim();
  if (props.busy || !title) return;
  emit('confirm', { title });
}
</script>
