<template>
  <div ref="root" class="relative">
    <button type="button" class="pill" :class="{ 'pill--open': open }" :aria-expanded="open" aria-haspopup="true" @click="open = !open">
      <i v-if="icon" :class="`pi ${icon} text-xs text-sky-300`"></i>
      <span>{{ label }}</span>
      <i class="pi pi-chevron-down text-[10px] text-slate-500"></i>
    </button>
    <div v-if="open" class="popover" :class="align === 'end' ? 'right-0' : 'left-0'">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

withDefaults(defineProps<{ label: string; icon?: string; align?: "start" | "end" }>(), { icon: "", align: "start" });

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
.pill:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
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
