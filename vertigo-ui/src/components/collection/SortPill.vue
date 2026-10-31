<template>
  <div ref="root" class="relative">
    <button type="button" class="pill" :class="{ 'pill--open': open }" :aria-expanded="open" aria-haspopup="listbox" @click="open = !open">
      <span class="truncate">Sort: {{ active?.label ?? orderBy }}</span>
      <i :class="`pi ${dirIcon} pill__dir`" aria-hidden="true"></i>
    </button>

    <!-- One row per key. The active key wears the arrow; picking it again turns the arrow round. -->
    <div v-if="open" class="popover" role="listbox" aria-label="Sort">
      <ul class="popover__list">
        <template v-for="(option, index) in options" :key="option.value">
          <li v-if="index > 0 && option.group !== options[index - 1].group" class="popover__sep" role="separator"></li>
          <li>
            <button type="button" class="popover__item" :class="{ 'popover__item--on': option.value === orderBy }" role="option"
              :aria-selected="option.value === orderBy" @click="pick(option)">
              <span class="truncate">{{ option.label }}</span>
              <i v-if="option.value === orderBy" :class="`pi ${dirIcon} pill__dir`" aria-hidden="true"></i>
            </button>
          </li>
        </template>
      </ul>
      <p class="popover__hint">Pick the active sort again to flip it.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

export type SortDir = "asc" | "desc";
export interface SortOption {
  label: string;
  value: string;
  defaultDir: SortDir;
  group: string;
}

const props = defineProps<{ options: SortOption[]; orderBy: string; orderDir: string }>();
const emit = defineEmits<{ (e: "update:sort", sort: { orderBy: string; orderDir: SortDir }): void }>();

const root = ref<HTMLElement | null>(null);
const open = ref(false);

const active = computed(() => props.options.find((o) => o.value === props.orderBy));
const dirIcon = computed(() => (props.orderDir === "asc" ? "pi-arrow-up" : "pi-arrow-down"));

function pick(option: SortOption) {
  if (option.value === props.orderBy) {
    emit("update:sort", { orderBy: option.value, orderDir: props.orderDir === "asc" ? "desc" : "asc" });
  } else {
    emit("update:sort", { orderBy: option.value, orderDir: option.defaultDir });
  }
  open.value = false;
}

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
  max-width: 16rem;
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

.pill__dir { font-size: 12px; color: #7dd3fc; }

.popover {
  position: absolute;
  right: 0;
  z-index: 60;
  top: calc(100% + 6px);
  width: 15rem;
  padding: 6px;
  border-radius: 12px;
  border: 1px solid #334155;
  background: #0f172a;
  box-shadow: 0 18px 40px -12px rgba(0, 0, 0, 0.7);
}
.popover__list { max-height: min(60vh, 34rem); overflow-y: auto; scrollbar-width: thin; scrollbar-color: #475569 transparent; }
.popover__sep { margin: 4px 8px; border-top: 1px solid rgba(255, 255, 255, 0.08); }
.popover__item {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 10px;
  border-radius: 8px;
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 600;
  text-align: left;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.popover__item:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.popover__item--on { color: #fff; }
.popover__hint { padding: 8px 10px 4px; color: #64748b; font-size: 12px; font-weight: 600; }

@media (prefers-reduced-motion: reduce) {
  .pill, .popover__item { transition: none; }
}
</style>
