<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="pill"
      :class="{ 'pill--active': hasValue, 'pill--open': open }"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span class="truncate">{{ hasValue ? `${label}: ${selectedLabel}` : label }}</span>
      <span v-if="hasValue && clearable" class="pill__clear" role="button" :aria-label="`Clear ${label}`" @click.stop="select('')">
        <i class="pi pi-times text-[10px]"></i>
      </span>
      <i v-else class="pi pi-chevron-down text-[10px] text-slate-500"></i>
    </button>

    <div v-if="open" class="popover" role="listbox" :aria-label="label">
      <div v-if="searchable" class="popover__search">
        <i class="pi pi-search text-xs text-slate-500"></i>
        <input ref="searchInput" v-model="term" type="text" :placeholder="`Find ${label.toLowerCase()}`" @keydown.escape.prevent="close" />
      </div>
      <ul class="popover__list">
        <li v-if="clearable && hasValue">
          <button type="button" class="popover__item text-slate-400" @click="select('')">Any {{ label.toLowerCase() }}</button>
        </li>
        <li v-for="option in filtered" :key="option.value">
          <button type="button" class="popover__item" :class="{ 'popover__item--on': option.value === modelValue }" role="option" :aria-selected="option.value === modelValue" @click="select(option.value)">
            <span class="truncate">{{ option.label }}</span>
            <i v-if="option.value === modelValue" class="pi pi-check text-xs text-sky-300"></i>
          </button>
        </li>
        <li v-if="!filtered.length" class="px-3 py-2 text-sm text-slate-500">Nothing matches.</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";

export interface PillOption {
  label: string;
  value: string;
}

const props = withDefaults(
  defineProps<{
    label: string;
    options: PillOption[];
    modelValue: string;
    searchable?: boolean;
    clearable?: boolean;
  }>(),
  { searchable: false, clearable: true }
);
const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();

const root = ref<HTMLElement | null>(null);
const searchInput = ref<HTMLInputElement | null>(null);
const open = ref(false);
const term = ref("");

const hasValue = computed(() => props.modelValue !== "" && props.modelValue !== null && props.modelValue !== undefined);
const selectedLabel = computed(() => props.options.find((o) => o.value === props.modelValue)?.label ?? props.modelValue);
const filtered = computed(() => {
  const t = term.value.trim().toLowerCase();
  return t ? props.options.filter((o) => o.label.toLowerCase().includes(t)) : props.options;
});

function toggle() {
  open.value ? close() : openList();
}
async function openList() {
  open.value = true;
  term.value = "";
  await nextTick();
  searchInput.value?.focus();
}
function close() {
  open.value = false;
}
function select(value: string) {
  emit("update:modelValue", value);
  close();
}
function onDocumentClick(event: MouseEvent) {
  if (open.value && root.value && !root.value.contains(event.target as Node)) close();
}
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") close();
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
  max-width: 16rem;
  height: 36px;
  padding: 0 12px 0 14px;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  transition: border-color 0.12s ease, background-color 0.12s ease, color 0.12s ease;
}
.pill:hover, .pill--open { border-color: rgba(255, 255, 255, 0.22); color: #fff; }
.pill--active { border-color: rgba(56, 189, 248, 0.5); background: rgba(56, 189, 248, 0.1); color: #e0f2fe; }
.pill:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
.pill__clear {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 5px;
  color: #bae6fd;
}
.pill__clear:hover { background: rgba(56, 189, 248, 0.25); color: #fff; }

.popover {
  position: absolute;
  z-index: 60;
  top: calc(100% + 6px);
  left: 0;
  min-width: 15rem;
  max-width: 20rem;
  padding: 6px;
  border-radius: 12px;
  border: 1px solid #334155;
  background: #0f172a;
  box-shadow: 0 18px 40px -12px rgba(0, 0, 0, 0.7);
}
.popover__search {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 2px 2px 6px;
  padding: 0 10px;
  height: 34px;
  border-radius: 8px;
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.popover__search input { flex: 1; min-width: 0; background: transparent; border: 0; outline: none; color: #fff; font: inherit; font-size: 13px; }
.popover__search input::placeholder { color: #64748b; }
.popover__list { max-height: 16rem; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #475569 transparent; }
.popover__item {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #cbd5e1;
}
.popover__item:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.popover__item--on { color: #fff; }
</style>
