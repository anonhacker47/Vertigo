<template>
  <div ref="root" class="gs" :class="{ 'gs--open': open, 'gs--block': block, 'gs--wide': wide }" @keydown="onKeydown">
    <div class="gs__field">
      <i class="pi pi-search gs__icon" aria-hidden="true"></i>
      <input
        ref="input"
        v-model="query"
        type="text"
        class="gs__input"
        placeholder="Search"
        aria-label="Search your collection"
        autocomplete="off"
        spellcheck="false"
        role="combobox"
        :aria-expanded="open"
        aria-controls="gs-results"
        :aria-activedescendant="activeKey ?? undefined"
        @focus="onFocus"
        @input="onInput"
      />
      <button v-if="query" type="button" class="gs__clear" aria-label="Clear search" @click="clear(true)">
        <i class="pi pi-times"></i>
      </button>
      <kbd v-else-if="!block" class="gs__kbd" aria-hidden="true">/</kbd>
    </div>

    <div v-if="open" id="gs-results" class="gs__panel" role="listbox">
      <p v-if="loading && !flat.length" class="gs__empty">Searching…</p>
      <p v-else-if="!flat.length" class="gs__empty">Nothing matches “{{ query.trim() }}”.</p>
      <template v-for="group in groups" :key="group.key">
        <template v-if="group.items.length">
          <p class="gs__group">{{ group.label }}</p>
          <button
            v-for="item in group.items"
            :id="item.key"
            :key="item.key"
            type="button"
            class="gs__row"
            role="option"
            :aria-selected="item.key === activeKey"
            :class="{ 'is-active': item.key === activeKey }"
            @mousemove="activeKey = item.key"
            @click="go(item)"
          >
            <span class="gs__thumb" :class="{ 'gs__thumb--round': group.round }">
              <img v-if="item.thumbnail" :src="item.thumbnail" alt="" loading="lazy" />
              <span v-else>{{ item.initial }}</span>
            </span>
            <span class="min-w-0">
              <span class="gs__title">{{ item.title }}</span>
              <span class="gs__sub">{{ item.subtitle }}</span>
            </span>
          </button>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter, type RouteLocationRaw } from "vue-router";
import SearchService from "@/services/SearchService";
import { issueDisplayLabel } from "@/utils/issueTitle";
import type { SearchEntity, SearchResponse } from "@/types/search.types";

/**
 * `block`: fill the container with the results inline (the mobile drawer).
 * `wide`: fill the container but keep the results floating (the tablet overlay).
 * `autofocus`: focus the box as soon as it mounts.
 */
const props = defineProps<{ block?: boolean; wide?: boolean; autofocus?: boolean }>();
const emit = defineEmits<{
  (e: "navigate"): void;
  /** Escape on an empty box, or a click outside: whoever shows the box may want to hide it. */
  (e: "dismiss"): void;
  /** "/" was pressed while this box is not visible: the parent can show one that is. */
  (e: "summon"): void;
}>();

const router = useRouter();
const route = useRoute();

const root = ref<HTMLElement | null>(null);
const input = ref<HTMLInputElement | null>(null);
const query = ref("");
const open = ref(false);
const loading = ref(false);
const results = ref<SearchResponse | null>(null);
const activeKey = ref<string | null>(null);

interface Hit {
  key: string;
  title: string;
  subtitle: string;
  thumbnail: string | null;
  initial: string;
  to: RouteLocationRaw;
}
interface Group {
  key: string;
  label: string;
  round: boolean;
  items: Hit[];
}

const initial = (text: string) => (text.trim()[0] || "?").toUpperCase();

function entityHits(rows: SearchEntity[], kind: "Publisher" | "Creator" | "Character"): Hit[] {
  return rows.map((e) => ({
    key: `${kind.toLowerCase()}-${e.id}`,
    title: e.title,
    subtitle: kind,
    thumbnail: e.thumbnail,
    initial: initial(e.title),
    to: { name: `${kind}Detail`, params: { Id: e.id, Link: e.slug } },
  }));
}

const groups = computed<Group[]>(() => {
  const r = results.value;
  if (!r) return [];
  return [
    {
      key: "series",
      label: "Series",
      round: false,
      items: r.series.map((s) => {
        const unit = s.manga ? "volumes" : "issues";
        return {
          key: `series-${s.id}`,
          title: s.title,
          subtitle: [s.series_format, `${s.issue_count} ${unit}`, `${s.owned_count} owned`].filter(Boolean).join(" · "),
          thumbnail: s.thumbnail,
          initial: initial(s.title),
          to: { name: "SeriesDetail", params: { Id: s.id, Link: s.slug } },
        };
      }),
    },
    {
      key: "issues",
      label: "Issues",
      round: false,
      items: r.issues.map((i) => ({
        key: `issue-${i.id}`,
        title: issueDisplayLabel(i.title, i.number),
        subtitle: [i.series.title, i.is_owned ? "Owned" : null, i.is_read ? "Read" : null].filter(Boolean).join(" · "),
        thumbnail: i.thumbnail,
        initial: initial(i.series.title),
        to: { name: "IssueDetail", params: { seriesId: i.series.id, slug: i.series.slug, number: i.number } },
      })),
    },
    { key: "publishers", label: "Publishers", round: true, items: entityHits(r.publishers, "Publisher") },
    { key: "creators", label: "Creators", round: true, items: entityHits(r.creators, "Creator") },
    { key: "characters", label: "Characters", round: true, items: entityHits(r.characters, "Character") },
  ];
});
const flat = computed(() => groups.value.flatMap((g) => g.items));

// ---- fetching: short debounce, and a stale reply never overwrites a newer one
let timer: ReturnType<typeof setTimeout> | null = null;
let requestId = 0;

function onInput() {
  if (timer) clearTimeout(timer);
  const text = query.value.trim();
  if (!text) {
    results.value = null;
    open.value = false;
    return;
  }
  open.value = true;
  loading.value = true;
  timer = setTimeout(() => void fetchResults(text), 180);
}

async function fetchResults(text: string) {
  const id = ++requestId;
  try {
    const data = await SearchService.search(text, 5);
    if (id !== requestId) return;
    results.value = data;
    activeKey.value = null;
  } catch (error) {
    if (id === requestId) results.value = null;
    console.error("Search failed:", error);
  } finally {
    if (id === requestId) loading.value = false;
  }
}

function onFocus() {
  if (query.value.trim()) open.value = true;
}

function clear(refocus = false) {
  if (timer) clearTimeout(timer);
  requestId++;
  query.value = "";
  results.value = null;
  activeKey.value = null;
  open.value = false;
  loading.value = false;
  if (refocus) input.value?.focus();
}

function close() {
  open.value = false;
  activeKey.value = null;
}

function go(item: Hit) {
  router.push(item.to);
  clear();
  input.value?.blur();
  emit("navigate");
}

// ---- keyboard: arrows walk the list, Enter opens the active (or first) hit, Escape backs out
function onKeydown(event: KeyboardEvent) {
  if (event.key === "Escape") {
    if (query.value) clear(true);
    else {
      input.value?.blur();
      emit("dismiss");
    }
    event.preventDefault();
    return;
  }
  if (!open.value) return;
  const keys = flat.value.map((h) => h.key);
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    if (!keys.length) return;
    const index = activeKey.value ? keys.indexOf(activeKey.value) : -1;
    const step = event.key === "ArrowDown" ? 1 : -1;
    activeKey.value = keys[(index + step + keys.length) % keys.length];
    document.getElementById(activeKey.value)?.scrollIntoView({ block: "nearest" });
    event.preventDefault();
  } else if (event.key === "Enter") {
    const hit = flat.value.find((h) => h.key === activeKey.value) ?? flat.value[0];
    if (hit) go(hit);
    event.preventDefault();
  }
}

// "/" anywhere on the page jumps to the box, like GitHub; typing in a field is left alone.
function onGlobalKey(event: KeyboardEvent) {
  if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey) return;
  const target = event.target as HTMLElement | null;
  if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
  event.preventDefault();
  if (!input.value) return;
  if (input.value.offsetParent === null) emit("summon");
  else input.value.focus();
}

function onPointerDown(event: MouseEvent) {
  if (root.value && !root.value.contains(event.target as Node)) {
    close();
    emit("dismiss");
  }
}

onMounted(() => {
  document.addEventListener("mousedown", onPointerDown);
  if (!props.block) document.addEventListener("keydown", onGlobalKey);
  if (props.autofocus) input.value?.focus();
});
onUnmounted(() => {
  document.removeEventListener("mousedown", onPointerDown);
  if (!props.block) document.removeEventListener("keydown", onGlobalKey);
  if (timer) clearTimeout(timer);
});

watch(() => route.fullPath, () => close());
</script>

<style scoped>
.gs {
  position: relative;
  width: 100%;
  max-width: 14rem;
  transition: max-width 0.15s ease;
}
.gs:focus-within,
.gs--open {
  max-width: 20rem;
}
.gs--block,
.gs--block:focus-within,
.gs--block.gs--open,
.gs--wide,
.gs--wide:focus-within,
.gs--wide.gs--open {
  max-width: none;
}

.gs__field {
  position: relative;
  display: flex;
  align-items: center;
}
.gs__icon {
  position: absolute;
  left: 11px;
  font-size: 13px;
  color: #94a3b8;
  pointer-events: none;
}
.gs__input {
  width: 100%;
  height: 36px;
  padding: 0 34px 0 32px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(11, 18, 32, 0.75);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}
.gs__input::placeholder {
  color: #64748b;
  font-weight: 500;
}
.gs__input:focus {
  outline: none;
  border-color: #38bdf8;
  background: #0b1220;
}
.gs__kbd,
.gs__clear {
  position: absolute;
  right: 8px;
  display: grid;
  place-items: center;
  height: 20px;
  min-width: 20px;
  border-radius: 5px;
  color: #94a3b8;
  font-size: 11px;
}
.gs__kbd {
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-family: inherit;
  font-weight: 700;
}
.gs__clear {
  cursor: pointer;
}
.gs__clear:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.gs__panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 60;
  max-height: min(70vh, 32rem);
  overflow-y: auto;
  padding: 6px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(11, 18, 32, 0.98);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55);
}
.gs--block .gs__panel {
  position: static;
  margin-top: 8px;
  max-height: none;
  box-shadow: none;
}
.gs__group {
  padding: 8px 10px 4px;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.gs__row {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 9px;
  text-align: left;
  cursor: pointer;
}
.gs__row.is-active {
  background: #1e293b;
}
.gs__thumb {
  display: grid;
  place-items: center;
  width: 30px;
  height: 42px;
  flex: none;
  overflow: hidden;
  border-radius: 5px;
  background: #1e293b;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 800;
}
.gs__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.gs__thumb--round {
  width: 34px;
  height: 34px;
  border-radius: 999px;
}
.gs__title,
.gs__sub {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gs__title {
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
.gs__sub {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
}
.gs__empty {
  padding: 14px 10px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
}

@media (prefers-reduced-motion: reduce) {
  .gs {
    transition: none;
  }
}
</style>
