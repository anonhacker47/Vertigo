<template>
  <div class="flex flex-wrap items-center gap-2">
    <label class="search">
      <i class="pi pi-search text-xs text-slate-500"></i>
      <input v-model="term" type="search" placeholder="Search series" aria-label="Search series" @keydown.enter.prevent="flush" />
      <button v-if="term" type="button" class="search__clear" aria-label="Clear search" @click="term = ''; flush()">
        <i class="pi pi-times text-[10px]"></i>
      </button>
    </label>

    <FilterPill label="Publisher" :options="options.publisher" :model-value="filters.publisher || ''" searchable @update:model-value="set('publisher', $event)" />
    <FilterPill label="Creator" :options="options.creator" :model-value="filters.creator || ''" searchable @update:model-value="set('creator', $event)" />
    <FilterPill label="Character" :options="options.character" :model-value="filters.character || ''" searchable @update:model-value="set('character', $event)" />
    <FilterPill label="Genre" :options="options.genre" :model-value="filters.genre || ''" searchable @update:model-value="set('genre', $event)" />
    <FilterPill label="Format" :options="options.series_format" :model-value="filters.series_format || ''" @update:model-value="set('series_format', $event)" />
    <button v-if="activeCount" type="button" class="h-9 px-2 text-[13px] font-bold text-sky-400 hover:text-sky-300" @click="$emit('clear')">Clear all</button>

    <div class="ml-auto flex flex-wrap items-center gap-2">
      <FilterPill label="Sort" :options="SORTS" :model-value="sortKey" :clearable="false" @update:model-value="setSort" />

      <div class="viewtoggle" role="group" aria-label="View">
        <button type="button" :aria-pressed="viewMode === 'card'" aria-label="Card view" title="Cards" @click="$emit('update:viewMode', 'card')"><i class="pi pi-th-large"></i></button>
        <button type="button" :aria-pressed="viewMode === 'list'" aria-label="List view" title="List" @click="$emit('update:viewMode', 'list')"><i class="pi pi-list"></i></button>
      </div>

      <PillMenu label="Display" icon="pi-sliders-h" align="end">
        <div v-if="viewMode === 'card'" class="mb-4">
          <div class="mb-2 flex items-baseline justify-between text-[13px] font-bold text-slate-300">
            <span>Cards per row</span><span class="tabular-nums text-slate-400">{{ cardsPerLine }}</span>
          </div>
          <input type="range" min="2" max="10" step="1" :value="cardsPerLine" class="range range-xs range-primary w-full" aria-label="Cards per row"
            @input="$emit('update:cardsPerLine', Number(($event.target as HTMLInputElement).value))" />
        </div>
        <div>
          <div class="mb-2 text-[13px] font-bold text-slate-300">Per page</div>
          <SegmentedControl :model-value="String(itemsPerPage)" :options="PAGE_SIZES" label="Items per page" @update:model-value="$emit('update:itemsPerPage', Number($event))" />
        </div>
      </PillMenu>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ViewMode } from "@/store/userPreferences";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import SeriesService from "@/services/SeriesService";
import FilterPill, { type PillOption } from "./FilterPill.vue";
import PillMenu from "./PillMenu.vue";
import SegmentedControl from "@/components/common/SegmentedControl.vue";

export interface SeriesFilters {
  query?: string;
  publisher?: string;
  creator?: string;
  character?: string;
  genre?: string;
  series_format?: string;
}

const props = defineProps<{
  filters: SeriesFilters;
  orderBy: string;
  orderDir: string;
  viewMode: ViewMode;
  cardsPerLine: number;
  itemsPerPage: number;
}>();
const emit = defineEmits<{
  (e: "update:filters", filters: SeriesFilters): void;
  (e: "update:sort", sort: { orderBy: string; orderDir: string }): void;
  (e: "update:viewMode", mode: ViewMode): void;
  (e: "update:cardsPerLine", n: number): void;
  (e: "update:itemsPerPage", n: number): void;
  (e: "clear"): void;
}>();

const SORTS: PillOption[] = [
  { label: "Newest first", value: "timestamp:desc" },
  { label: "Oldest first", value: "timestamp:asc" },
  { label: "Title A–Z", value: "title:asc" },
  { label: "Title Z–A", value: "title:desc" },
];
const PAGE_SIZES = [10, 25, 50, 100].map((n) => ({ label: String(n), value: String(n) }));
const FIELDS = ["publisher", "creator", "character", "genre", "series_format"] as const;

const options = ref<Record<(typeof FIELDS)[number], PillOption[]>>({ publisher: [], creator: [], character: [], genre: [], series_format: [] });

const sortKey = computed(() => `${props.orderBy}:${props.orderDir}`);
const activeCount = computed(() => FIELDS.filter((f) => props.filters[f]).length + (props.filters.query ? 1 : 0));

function set(field: (typeof FIELDS)[number], value: string) {
  emit("update:filters", { ...props.filters, [field]: value });
}
function setSort(key: string) {
  const [orderBy, orderDir] = key.split(":");
  emit("update:sort", { orderBy, orderDir });
}

const term = ref(props.filters.query ?? "");
let timer: ReturnType<typeof setTimeout> | null = null;
function flush() {
  if (timer) clearTimeout(timer);
  timer = null;
  if ((props.filters.query ?? "") !== term.value) emit("update:filters", { ...props.filters, query: term.value });
}
watch(term, () => {
  if (timer) clearTimeout(timer);
  timer = setTimeout(flush, 300);
});
watch(() => props.filters.query, (q) => { if ((q ?? "") !== term.value) term.value = q ?? ""; });
onBeforeUnmount(() => { if (timer) clearTimeout(timer); });

onMounted(async () => {
  for (const field of FIELDS) {
    try {
      const response = await SeriesService.getSeriesFieldValues(field);
      options.value[field] = (response.data as any[]).map((item) => {
        const value = typeof item === "string" ? item : item.value;
        return { label: String(value), value: String(value) };
      });
    } catch (error) {
      console.error(error);
    }
  }
});
</script>

<style scoped>
.search {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  width: 15rem;
  max-width: 100%;
  padding: 0 10px 0 14px;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  transition: border-color 0.12s ease;
}
.search:focus-within { border-color: rgba(56, 189, 248, 0.6); }
.search input { flex: 1; min-width: 0; background: transparent; border: 0; outline: none; color: #fff; font: inherit; font-size: 13px; font-weight: 600; }
.search input::placeholder { color: #64748b; }
.search input::-webkit-search-cancel-button { display: none; }
.search__clear { display: inline-flex; width: 18px; height: 18px; align-items: center; justify-content: center; border-radius: 5px; color: #94a3b8; }
.search__clear:hover { background: rgba(255, 255, 255, 0.1); color: #fff; }

.viewtoggle { display: inline-flex; gap: 2px; padding: 3px; border-radius: 5px; border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.03); }
.viewtoggle button { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; border-radius: 5px; color: #94a3b8; font-size: 12px; }
.viewtoggle button:hover { color: #fff; }
.viewtoggle button[aria-pressed="true"] { background: #1e293b; color: #fff; }
.viewtoggle button:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
</style>
