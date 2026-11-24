<template>
  <div class="flex flex-wrap items-center gap-2">
    <div class="lead">
      <label class="search">
        <i class="pi pi-search text-xs text-slate-500"></i>
        <input v-model="term" type="search" placeholder="Search series" aria-label="Search series" @keydown.enter.prevent="flush" />
        <button v-if="term" type="button" class="search__clear" aria-label="Clear search" @click="term = ''; flush()">
          <i class="pi pi-times text-[10px]"></i>
        </button>
      </label>

      <PillMenu label="Filters" icon="pi-filter" :count="chips.length" wide>
        <div class="panel">
          <div class="panel__label">Series</div>
          <div class="panel__picks">
            <FilterPill v-for="pick in PICKS" :key="pick.field" :label="pick.label" :options="options[pick.field]" :model-value="filters[pick.field] || ''"
              :searchable="pick.searchable" @update:model-value="set(pick.field, $event)" />
          </div>

          <template v-for="group in STATUS_GROUPS" :key="group.field">
            <div class="panel__label">{{ group.label }}</div>
            <div class="choices" role="group" :aria-label="group.label">
              <button v-for="option in group.options" :key="option.value" type="button" class="choice" :aria-pressed="filters[group.field] === option.value"
                @click="toggle(group.field, option.value)">{{ option.label }}</button>
            </div>
          </template>

          <div class="panel__label">Rating</div>
          <div class="flex items-center gap-3">
            <div class="stars" role="group" aria-label="Minimum rating">
              <button v-for="n in 5" :key="n" type="button" :aria-pressed="minRating === n" :aria-label="`${n} stars or more`" @click="toggle('min_rating', String(n))">
                <i class="pi" :class="n <= minRating ? 'pi-star-fill text-sky-400' : 'pi-star text-slate-600'"></i>
              </button>
            </div>
            <span class="text-[13px] font-semibold text-slate-400">{{ minRating ? ratingLabel(minRating) : "Any" }}</span>
          </div>
        </div>
      </PillMenu>
    </div>

    <div class="toolbar__right ml-auto flex flex-wrap items-center gap-2">
      <SortPill :options="SORTS" :order-by="orderBy" :order-dir="orderDir" @update:sort="$emit('update:sort', $event)" />

      <div class="viewtoggle" role="group" aria-label="View">
        <button type="button" :aria-pressed="viewMode === 'card'" aria-label="Card view" title="Cards" @click="$emit('update:viewMode', 'card')"><i class="pi pi-th-large"></i></button>
        <button type="button" :aria-pressed="viewMode === 'list'" aria-label="List view" title="List" @click="$emit('update:viewMode', 'list')"><i class="pi pi-list"></i></button>
        <button type="button" :aria-pressed="viewMode === 'longbox'" aria-label="Longbox view" title="Longbox" @click="$emit('update:viewMode', 'longbox')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 10h18v10H3z" /><path d="m7 10 1.5-5h7L17 10" /><path d="M10.5 10V5M13.5 10V5" />
          </svg>
        </button>
      </div>

      <PillMenu v-if="viewMode !== 'longbox'" label="Display" icon="pi-sliders-h" align="end">
        <div v-if="viewMode === 'card'" class="mb-4">
          <div class="mb-2 flex items-baseline justify-between text-[13px] font-bold text-slate-300">
            <span>Cards per row</span><span class="tabular-nums text-slate-400">{{ cardsPerLine }}</span>
          </div>
          <input type="range" :min="cardsPerLineRange.min" :max="cardsPerLineRange.max" step="1" :value="cardsPerLine" class="range range-xs range-primary w-full" aria-label="Cards per row"
            @input="$emit('update:cardsPerLine', Number(($event.target as HTMLInputElement).value))" />
        </div>
        <div>
          <div class="mb-2 text-[13px] font-bold text-slate-300">Per page</div>
          <SegmentedControl :model-value="String(itemsPerPage)" :options="PAGE_SIZES" label="Items per page" @update:model-value="$emit('update:itemsPerPage', Number($event))" />
        </div>
      </PillMenu>
    </div>

    <div v-if="chips.length" class="flex basis-full flex-wrap items-center gap-2">
      <button v-for="chip in chips" :key="chip.field" type="button" class="chip" :aria-label="`Remove ${chip.text}`" @click="set(chip.field, '')">
        <span class="truncate">{{ chip.text }}</span>
        <i class="pi pi-times text-[10px]"></i>
      </button>
      <button type="button" class="px-1 text-[13px] font-bold text-sky-400 hover:text-sky-300" @click="$emit('clear')">Clear all</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ViewMode } from "@/store/userPreferences";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import SeriesService from "@/services/SeriesService";
import FilterPill, { type PillOption } from "./FilterPill.vue";
import SortPill, { type SortOption } from "./SortPill.vue";
import PillMenu from "./PillMenu.vue";
import SegmentedControl from "@/components/common/SegmentedControl.vue";
import { SERIES_FILTER_KEYS, type SeriesFilterFields, type SeriesFilterKey } from "@/types/series-filter.types";

export type SeriesFilters = SeriesFilterFields;

const props = defineProps<{
  filters: SeriesFilters;
  orderBy: string;
  orderDir: string;
  viewMode: ViewMode;
  cardsPerLine: number;
  cardsPerLineRange: { min: number; max: number };
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

// Keys the collection endpoint accepts (see series_sorts.py), grouped: what it is, how far along, when, and yours.
const SORTS: SortOption[] = [
  { label: "Title", value: "title", defaultDir: "asc", group: "what" },
  { label: "Publisher", value: "publisher", defaultDir: "asc", group: "what" },
  { label: "Format", value: "series_format", defaultDir: "asc", group: "what" },
  { label: "Date added", value: "timestamp", defaultDir: "desc", group: "what" },
  { label: "Issues", value: "issue_count", defaultDir: "desc", group: "progress" },
  { label: "Owned", value: "owned_count", defaultDir: "desc", group: "progress" },
  { label: "Collected", value: "collected", defaultDir: "desc", group: "progress" },
  { label: "Read", value: "read", defaultDir: "desc", group: "progress" },
  { label: "Missing", value: "missing", defaultDir: "desc", group: "progress" },
  { label: "Unread on the shelf", value: "unread", defaultDir: "desc", group: "progress" },
  { label: "Last bought", value: "last_bought", defaultDir: "desc", group: "when" },
  { label: "Last read", value: "last_read", defaultDir: "desc", group: "when" },
  { label: "Rating", value: "user_rating", defaultDir: "desc", group: "yours" },
  { label: "Spent", value: "purchase_cost", defaultDir: "desc", group: "yours" },
];
const PAGE_SIZES = [10, 25, 50, 100].map((n) => ({ label: String(n), value: String(n) }));
const FIELDS = ["publisher", "creator", "character", "genre", "series_format"] as const;

type PickField = (typeof FIELDS)[number];
const PICKS: { field: PickField; label: string; searchable: boolean }[] = [
  { field: "publisher", label: "Publisher", searchable: true },
  { field: "creator", label: "Creator", searchable: true },
  { field: "character", label: "Character", searchable: true },
  { field: "genre", label: "Genre", searchable: true },
  { field: "series_format", label: "Format", searchable: false },
];

// Values the collection endpoint accepts (see series_filters.py).
const STATUS_GROUPS: { field: SeriesFilterKey; label: string; options: PillOption[] }[] = [
  { field: "collection", label: "Status", options: [
    { label: "Owned", value: "owned" },
    { label: "Complete", value: "complete" },
    { label: "Incomplete", value: "incomplete" },
    { label: "Not owned", value: "not_owned" },
  ] },
  { field: "reading", label: "Reading", options: [
    { label: "Read", value: "read" },
    { label: "In progress", value: "in_progress" },
    { label: "Unread", value: "unread" },
  ] },
  { field: "type", label: "Type", options: [
    { label: "Comic", value: "comic" },
    { label: "Manga", value: "manga" },
  ] },
];

const options = ref<Record<PickField, PillOption[]>>({ publisher: [], creator: [], character: [], genre: [], series_format: [] });

const minRating = computed(() => Number(props.filters.min_rating) || 0);
const ratingLabel = (n: number) => (n >= 5 ? "5 stars" : `${n}+ stars`);

// One removable chip per active filter; the search term stays in its own box.
const chips = computed(() => {
  const list: { field: SeriesFilterKey; text: string }[] = [];
  for (const pick of PICKS) {
    const value = props.filters[pick.field];
    if (value) list.push({ field: pick.field, text: `${pick.label}: ${value}` });
  }
  for (const group of STATUS_GROUPS) {
    const value = props.filters[group.field];
    if (value) list.push({ field: group.field, text: `${group.label}: ${group.options.find((o) => o.value === value)?.label ?? value}` });
  }
  if (minRating.value) list.push({ field: "min_rating", text: ratingLabel(minRating.value) });
  return list;
});

function toggle(field: SeriesFilterKey, value: string) {
  set(field, props.filters[field] === value ? "" : value);
}

function set(field: SeriesFilterKey, value: string) {
  emit("update:filters", { ...props.filters, [field]: value });
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
  try {
    const { data } = await SeriesService.getSeriesFilterValues();
    for (const field of FIELDS) {
      options.value[field] = ((data[field] ?? []) as { value: string }[]).map((item) => ({ label: String(item.value), value: String(item.value) }));
    }
  } catch (error) {
    console.error(error);
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
.viewtoggle svg { width: 14px; height: 14px; }
.viewtoggle button[aria-pressed="true"] { background: #1e293b; color: #fff; }
.viewtoggle button:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }

.lead { position: relative; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; max-width: 100%; }

.panel { display: grid; grid-template-columns: 4.5rem minmax(0, 1fr); align-items: center; gap: 14px 12px; }
.panel__label { color: #94a3b8; font-size: 13px; font-weight: 700; }
.panel__label:first-child { align-self: start; line-height: 36px; }
.panel__picks { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.panel__picks > * { min-width: 0; }
.panel__picks :deep(.pill) { width: 100%; max-width: none; justify-content: space-between; }
.panel__picks > :nth-child(even) :deep(.popover) { left: auto; right: 0; }
.choices { display: flex; flex-wrap: wrap; gap: 6px; }
.choice {
  height: 30px;
  padding: 0 12px;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  transition: border-color 0.12s ease, background-color 0.12s ease, color 0.12s ease;
}
.choice:hover { border-color: rgba(255, 255, 255, 0.22); color: #fff; }
.choice[aria-pressed="true"] { border-color: rgba(56, 189, 248, 0.5); background: rgba(56, 189, 248, 0.1); color: #e0f2fe; }
.choice:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }

.stars { display: inline-flex; gap: 2px; }
.stars button { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; border-radius: 5px; font-size: 15px; }
.stars button:hover { background: rgba(255, 255, 255, 0.06); }
.stars button:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }

.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 18rem;
  height: 28px;
  padding: 0 8px 0 10px;
  border-radius: 5px;
  border: 1px solid rgba(56, 189, 248, 0.4);
  background: rgba(56, 189, 248, 0.1);
  color: #e0f2fe;
  font-size: 12px;
  font-weight: 700;
}
.chip:hover { background: rgba(56, 189, 248, 0.2); color: #fff; }
.chip:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }

@media (max-width: 767px) {
  .lead { width: 100%; flex-wrap: nowrap; }
  .search { flex: 1 1 0; width: auto; min-width: 0; }
  .panel { grid-template-columns: minmax(0, 1fr); gap: 8px; }
  .panel__label:first-child { line-height: inherit; }
  .panel__label:not(:first-child) { margin-top: 10px; }
  .choice { height: 34px; }
  .stars button { width: 36px; height: 36px; font-size: 18px; }
  .toolbar__right { width: 100%; margin-left: 0; flex-wrap: nowrap; }
  .toolbar__right > :first-child { flex: 1 1 auto; min-width: 0; }
  .toolbar__right > :first-child :deep(.pill) { width: 100%; justify-content: space-between; }
  .toolbar__right > :first-child :deep(.popover) { left: 0; right: auto; }
  .toolbar__right > :last-child { margin-left: auto; }
}
</style>
