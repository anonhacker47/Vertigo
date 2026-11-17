<template>
  <div ref="root" :class="{ relative: !wide }">
    <button type="button" class="pill" :class="{ 'pill--open': open, 'pill--active': count }" :aria-expanded="open" aria-haspopup="true" @click="open = !open">
      <i v-if="icon" :class="`pi ${icon} text-xs text-sky-300`"></i>
      <span>{{ label }}</span>
      <span v-if="count" class="pill__count">{{ count }}</span>
      <i v-else class="pi pi-chevron-down text-[10px] text-slate-500"></i>
    </button>
    <div v-if="open" class="popover" :class="[align === 'end' ? 'right-0' : 'left-0', { 'popover--wide': wide }]">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

// wide: a broad panel hung from the nearest positioned ancestor, not from the pill
withDefaults(defineProps<{ label: string; icon?: string; align?: "start" | "end"; count?: number; wide?: boolean }>(), { icon: "", align: "start", count: 0, wide: false });

const root = ref<HTMLElement | null>(null);
const open = ref(false);

function onDocumentClick(event: MouseEvent) {
  if (open.value && root.value && !root.value.contains(event.target as Node)) open.value = false;
}
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") open.value = false;
}
onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKey);
});
</script>

<style scoped>
.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 12px 0 14px;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  transition: border-color 0.12s ease, color 0.12s ease;
}
.pill:hover, .pill--open { border-color: rgba(255, 255, 255, 0.22); color: #fff; }
.pill--active { border-color: rgba(56, 189, 248, 0.5); background: rgba(56, 189, 248, 0.1); color: #e0f2fe; }
.pill:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
.pill__count {
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: #38bdf8;
  color: #0b1220;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
.popover.popover--wide { width: min(34rem, calc(100vw - 2rem)); padding: 16px; }
.popover {
  position: absolute;
  z-index: 60;
  top: calc(100% + 6px);
  width: 17rem;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid #334155;
  background: #0f172a;
  box-shadow: 0 18px 40px -12px rgba(0, 0, 0, 0.7);
}
</style>
