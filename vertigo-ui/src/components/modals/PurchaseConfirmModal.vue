<template>
  <div v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md transition-all duration-200">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl relative">
      <h3 class="text-lg font-bold text-white mb-5">Add Purchase Details</h3>


      <div class="flex flex-col gap-4 mb-6">
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Bought Date</label>
          <div class="relative rounded-xl shadow-sm">
            <input type="date" v-model="localDate"
              class="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-4 text-white placeholder-slate-600 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary text-sm [color-scheme:dark]"
              @keyup.enter="handleConfirm" />
          </div>
        </div>

                <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Purchase Price</label>
          <div class="relative rounded-xl shadow-sm">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2">
              <span class="text-slate-400 font-semibold text-sm">{{ currency || '₹' }}</span>
            </div>
            <input type="number" v-model="localPrice" placeholder="0.00" step="0.01" min="0"
              class="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 pl-10 pr-4 text-white placeholder-slate-600 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary text-sm"
              @keyup.enter="handleConfirm" ref="inputRef" />
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 justify-end border-t border-slate-800/60 pt-4">
        <button @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition">
          Cancel
        </button>
        <button @click="handleConfirm"
          class="px-5 py-2 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition shadow-lg shadow-emerald-500/10">
          Mark as Owned
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';

const props = defineProps<{
  show: boolean;
  currency?: string;
  initialPrice?: number | null;
  initialDate?: string | null;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'confirm', payload: { price: number | null; date: string | null }): void;
}>();

const localPrice = ref<number | null>(null);
const localDate = ref<string>("");
const inputRef = ref<HTMLInputElement | null>(null);

watch(() => props.show, (isShowing) => {
  if (isShowing) {
    localPrice.value = props.initialPrice ?? null;
    localDate.value = props.initialDate ? props.initialDate.substring(0, 10) : "";

    nextTick(() => {
      inputRef.value?.focus();
    });
  }
});

function handleConfirm() {
  const finalPrice = localPrice.value !== null && !isNaN(Number(localPrice.value))
    ? Number(localPrice.value)
    : null;

  const finalDate = localDate.value ? new Date(localDate.value).toISOString() : null;

  emit('confirm', {
    price: finalPrice,
    date: finalDate
  });
}
</script>