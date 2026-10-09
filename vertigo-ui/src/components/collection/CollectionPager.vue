<template>
  <nav v-if="total > limit" class="flex flex-wrap items-center justify-center gap-4 py-8" aria-label="Pages">
    <span class="text-sm font-semibold text-slate-400 tabular-nums">{{ from }}–{{ to }} of {{ total }}</span>
    <div class="flex items-center gap-1">
      <button type="button" class="pg pg--arrow" :disabled="page === 1" aria-label="Previous page" @click="go(page - 1)">
        <i class="pi pi-chevron-left text-xs"></i>
      </button>
      <template v-for="(p, i) in pages" :key="i">
        <span v-if="p === '…'" class="px-1 text-slate-500">…</span>
        <button v-else type="button" class="pg" :class="{ 'pg--on': p === page }" :aria-current="p === page ? 'page' : undefined" @click="go(p as number)">{{ p }}</button>
      </template>
      <button type="button" class="pg pg--arrow" :disabled="page === pageCount" aria-label="Next page" @click="go(page + 1)">
        <i class="pi pi-chevron-right text-xs"></i>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ total: number; limit: number; offset: number }>();
const emit = defineEmits<{ (e: "page", payload: { first: number; rows: number }): void }>();

const pageCount = computed(() => Math.max(1, Math.ceil(props.total / props.limit)));
const page = computed(() => Math.floor(props.offset / props.limit) + 1);
const from = computed(() => (props.total ? props.offset + 1 : 0));
const to = computed(() => Math.min(props.offset + props.limit, props.total));

const pages = computed<(number | "…")[]>(() => {
  const n = pageCount.value, c = page.value;
  if (n <= 7) return Array.from({ length: n }, (_, i) => i + 1);
  const set = new Set<number>([1, n, c - 1, c, c + 1].filter((p) => p >= 1 && p <= n));
  const sorted = [...set].sort((a, b) => a - b);
  const out: (number | "…")[] = [];
  sorted.forEach((p, i) => {
    if (i && p - (sorted[i - 1] as number) > 1) out.push("…");
    out.push(p);
  });
  return out;
});

function go(p: number) {
  if (p < 1 || p > pageCount.value || p === page.value) return;
  emit("page", { first: (p - 1) * props.limit, rows: props.limit });
}
</script>

<style scoped>
.pg {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 10px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
  font-variant-numeric: tabular-nums;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.pg:hover:not(:disabled) { background: rgba(255, 255, 255, 0.06); color: #fff; }
.pg--on { background: #1e293b; color: #fff; }
.pg--arrow { color: #94a3b8; }
.pg:disabled { opacity: 0.35; cursor: default; }
.pg:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
</style>
