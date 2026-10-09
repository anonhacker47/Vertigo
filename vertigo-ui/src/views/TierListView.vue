<template>
  <div class="flex flex-col w-full bg-base-100 px-4 pb-4 md:px-8">
    <div class="flex flex-col gap-3 py-4 w-full max-w-page mx-auto lg:h-[calc(100dvh-var(--spacing-header))]">
      <div class="flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="flex flex-wrap items-center gap-4">
          <h1 class="text-2xl font-bold text-white leading-none">Tier List</h1>
          <SegmentedControl
            :model-value="mode"
            :options="TIER_LIST_MODES"
            label="Rank series or issues"
            @update:model-value="setMode($event as TierListMode)"
          />
        </div>
        <div class="flex gap-2 shrink-0">
          <button @click="autoRank" :disabled="loading" class="btn btn-primary btn-sm" title="Rank based on your ratings">
            <i class="pi pi-sparkles"></i><span class="hidden sm:inline">Auto Rank</span>
          </button>
          <button @click="resetTiers" :disabled="loading" class="btn btn-warning btn-sm" title="Move all to Deck">
            <i class="pi pi-refresh"></i><span class="hidden sm:inline">Reset</span>
          </button>
          <button @click="openExportModal" :disabled="loading" class="btn btn-success btn-sm" title="Download as Image">
            <i class="pi pi-download"></i><span class="hidden sm:inline">Download</span>
          </button>
        </div>
      </div>

      <!-- Tiers on the left, the deck as a column on the right: items drag straight across
           without scrolling the page. Below lg the deck stacks under the tiers. -->
      <div class="flex flex-col lg:flex-row gap-4 flex-1 min-h-0">
        <section class="flex flex-col gap-2 flex-1 min-w-0 min-h-0" aria-label="Tiers">
          <div v-if="loading" class="flex flex-1 items-center justify-center min-h-[24rem]">
            <span class="loading loading-ring text-success h-20 w-20"></span>
          </div>

          <template v-else>
            <div
              v-for="tier in tiers"
              :key="tier.id"
              class="flex rounded-md overflow-hidden border border-slate-700 bg-[#1a2332] min-h-[6rem] lg:flex-1 lg:min-h-0"
            >
              <div :class="['w-12 md:w-16 shrink-0 flex items-center justify-center', tier.color]">
                <span class="text-2xl md:text-3xl font-black text-black/80">{{ tier.name }}</span>
              </div>

              <draggable
                v-model="tier.items"
                item-key="id"
                :group="DRAG_GROUP"
                class="tier-row flex-1 min-w-0 flex flex-nowrap items-center gap-2 p-2 bg-base-200/50 overflow-x-auto overflow-y-hidden"
                ghost-class="opacity-50"
                @change="saveState"
                :force-fallback="true"
                :scroll-sensitivity="160"
                :scroll-speed="25"
                :fallback-tolerance="3"
              >
                <template #item="{ element }">
                  <TierTile :item="element" @open="open(element)" />
                </template>
              </draggable>
            </div>
          </template>
        </section>

        <aside
          class="flex flex-col shrink-0 rounded-md border border-slate-700 bg-base-300 lg:w-1/4 lg:min-w-[15rem] lg:max-w-sm lg:min-h-0"
          aria-label="Deck"
        >
          <div class="flex flex-col gap-2 p-3 border-b border-slate-700 shrink-0">
            <h3 class="text-base font-semibold text-white flex items-center gap-2">
              <i class="pi pi-inbox text-gray-400"></i> Deck
              <span class="badge badge-sm badge-primary">{{ filteredDeck.length }}</span>
            </h3>
            <div class="relative">
              <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
              <input v-model="deckSearch" type="search" class="input input-sm input-bordered w-full pl-9 bg-base-100"
                placeholder="Search deck" :aria-label="`Search ${mode}`" />
            </div>
          </div>

          <draggable
            v-model="deck"
            item-key="id"
            :group="DRAG_GROUP"
            class="deck-list flex flex-wrap content-start gap-2 p-3 min-h-40 max-h-[60vh] overflow-y-auto lg:flex-1 lg:min-h-0 lg:max-h-none"
            ghost-class="opacity-50"
            @change="saveState"
            :force-fallback="true"
            :scroll-sensitivity="160"
            :scroll-speed="25"
            :fallback-tolerance="3"
          >
            <template #item="{ element }">
              <TierTile v-show="matchesDeckFilter(element)" :item="element" @open="open(element)" />
            </template>
          </draggable>
          <p v-if="!loading && deck.length && !filteredDeck.length" class="px-3 pb-3 text-xs text-gray-400">
            Nothing in the deck matches.
          </p>
          <p v-else-if="!loading && !deck.length" class="px-3 pb-3 text-xs text-gray-400">
            Everything is ranked.
          </p>
        </aside>
      </div>
    </div>

    <TierListExportModal :show="showExportModal" :initial-title="exportTitle" :busy="exporting"
      @cancel="showExportModal = false" @confirm="exportImage" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import draggable from 'vuedraggable';
import { useToast } from 'primevue/usetoast';
import SegmentedControl from '@/components/common/SegmentedControl.vue';
import TierTile from '@/components/cards/TierTile.vue';
import TierListExportModal from '@/components/modals/TierListExportModal.vue';
import { loadTierItems, TIER_LIST_MODES, type TierItem, type TierListMode } from '@/utils/tierListItems';
import {
  renderTierListImage, tierListFileName, downloadBlob, isAbortError, type TierListImageTier,
} from '@/utils/tierListImage';

const router = useRouter();
const toast = useToast();
const loading = ref(true);

const DRAG_GROUP = 'tier-list';

interface Tier {
  id: string;
  name: string;
  color: string;
  exportColor: string;
  min: number;
  max: number;
  items: TierItem[];
}

const tiers = ref<Tier[]>([
  { id: 'S', color: 'bg-red-500', exportColor: '#fb2c36', name: 'S', min: 4.5, max: 5.0, items: [] },
  { id: 'A', color: 'bg-orange-500', exportColor: '#ff6900', name: 'A', min: 4.0, max: 4.49, items: [] },
  { id: 'B', color: 'bg-yellow-400', exportColor: '#fdc700', name: 'B', min: 3.0, max: 3.99, items: [] },
  { id: 'C', color: 'bg-green-500', exportColor: '#00c950', name: 'C', min: 2.0, max: 2.99, items: [] },
  { id: 'D', color: 'bg-blue-500', exportColor: '#2b7fff', name: 'D', min: 0, max: 1.99, items: [] },
]);

const deck = ref<TierItem[]>([]);

// ---------------------------------------------------------------- mode

// Each mode keeps its own saved layout. The series key predates the switch, so lists
// ranked before it carry over untouched.
const STATE_KEYS: Record<TierListMode, string> = { series: 'tierListState', issues: 'tierListIssuesState' };
const MODE_KEY = 'tierListMode';

const readMode = (): TierListMode => (localStorage.getItem(MODE_KEY) === 'issues' ? 'issues' : 'series');
const mode = ref<TierListMode>(readMode());

const itemCache = new Map<TierListMode, TierItem[]>();
let loadToken = 0;

const loadMode = async (target: TierListMode) => {
  const token = ++loadToken;
  loading.value = true;
  try {
    let items = itemCache.get(target);
    if (!items) {
      items = await loadTierItems(target);
      itemCache.set(target, items);
    }
    if (token !== loadToken) return;
    loadState(target, items);
  } catch (error) {
    if (token !== loadToken) return;
    tiers.value.forEach(t => t.items = []);
    deck.value = [];
    console.error(`Failed to load ${target} for the tier list:`, error);
    toast.add({
      severity: 'error',
      summary: 'Could not load the tier list',
      detail: `Your ${target} could not be fetched. Try again in a moment.`,
      life: 5000,
    });
  } finally {
    if (token === loadToken) loading.value = false;
  }
};

const setMode = (target: TierListMode) => {
  if (target === mode.value) return;
  mode.value = target;
  localStorage.setItem(MODE_KEY, target);
  deckSearch.value = '';
  loadMode(target);
};


const deckSearch = ref('');

const matchesDeckFilter = (item: TierItem) => {
  const q = deckSearch.value.trim().toLowerCase();
  return !q || item.searchText.includes(q);
};

const filteredDeck = computed(() => deck.value.filter(matchesDeckFilter));


const saveState = () => {
  if (loading.value) return; // never overwrite a saved layout with a half-loaded one
  const state = {
    tiers: tiers.value.map(t => ({ id: t.id, itemIds: t.items.map(i => i.id) })),
    deckItemIds: deck.value.map(i => i.id),
  };
  localStorage.setItem(STATE_KEYS[mode.value], JSON.stringify(state));
};

const loadState = (target: TierListMode, items: TierItem[]) => {
  const byId = new Map(items.map(i => [i.id, i]));
  const take = (ids: unknown): TierItem[] => {
    if (!Array.isArray(ids)) return [];
    const out: TierItem[] = [];
    for (const id of ids) {
      const item = typeof id === 'number' ? byId.get(id) : undefined;
      if (item) {
        out.push(item);
        byId.delete(item.id);
      }
    }
    return out;
  };

  let saved: any = null;
  try {
    saved = JSON.parse(localStorage.getItem(STATE_KEYS[target]) || 'null');
  } catch (e) {
    console.error('Failed to parse saved tier list state', e);
  }

  tiers.value.forEach(tier => {
    const savedTier = saved?.tiers?.find((t: any) => t?.id === tier.id);
    tier.items = take(savedTier?.itemIds ?? savedTier?.seriesIds);
  });
  deck.value = [...take(saved?.deckItemIds ?? saved?.deckSeriesIds), ...byId.values()];
};


const resetTiers = () => {
  deck.value = [...deck.value, ...tiers.value.flatMap(t => t.items)];
  tiers.value.forEach(t => t.items = []);
  saveState();
};

const autoRank = () => {
  const everything = [...deck.value, ...tiers.value.flatMap(t => t.items)];
  tiers.value.forEach(t => t.items = []);
  deck.value = [];

  everything.forEach(item => {
    const rating = item.rating;
    const target = rating != null && rating > 0
      ? tiers.value.find(t => rating >= t.min && rating <= t.max)
      : undefined;
    if (target) target.items.push(item);
    else deck.value.push(item);
  });

  tiers.value.forEach(t => {
    t.items.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  });

  saveState();
};

const open = (item: TierItem) => {
  router.push(item.route);
};


const EXPORT_TITLE_KEY = 'tierListExportTitle';
const showExportModal = ref(false);
const exporting = ref(false);
const exportTitle = ref(localStorage.getItem(EXPORT_TITLE_KEY) || 'My Tier List');

const exportTiers = computed<TierListImageTier[]>(() =>
  tiers.value.map(t => ({
    name: t.name,
    color: t.exportColor,
    covers: t.items.map(i => i.cover),
  }))
);

const openExportModal = () => {
  if (!loading.value) showExportModal.value = true;
};

let exportAbort: AbortController | null = null;
onBeforeUnmount(() => {
  exportAbort?.abort();
  loadToken++; // drop any fetch still in flight
});

const exportImage = async ({ title }: { title: string }) => {
  if (exporting.value) return;
  const controller = new AbortController();
  exportAbort = controller;
  exporting.value = true;
  try {
    const blob = await renderTierListImage(
      {
        title,
        tiers: exportTiers.value,
        footer: `Exported ${new Date().toLocaleDateString()}`,
      },
      { signal: controller.signal },
    );
    downloadBlob(blob, tierListFileName(title));
    exportTitle.value = title;
    localStorage.setItem(EXPORT_TITLE_KEY, title);
    showExportModal.value = false;
  } catch (error) {
    if (isAbortError(error) || controller.signal.aborted) return;
    console.error('Failed to render tier list image', error);
    toast.add({
      severity: 'error',
      summary: 'Download failed',
      detail: error instanceof Error ? error.message : 'Could not render the tier list image.',
      life: 5000,
    });
  } finally {
    if (exportAbort === controller) exportAbort = null;
    exporting.value = false;
  }
};

onMounted(() => loadMode(mode.value));
</script>

<style scoped>
.tier-row > .tier-tile {
  height: 5rem;
}
.deck-list > .tier-tile {
  height: 7rem;
}
@media (min-width: 64rem) {
  .tier-row > .tier-tile {
    height: 100%;
    max-height: 12rem;
  }
}

.tier-row,
.deck-list {
  scrollbar-width: thin;
  scrollbar-color: #475569 transparent;
}
.tier-row::-webkit-scrollbar {
  height: 6px;
}
.deck-list::-webkit-scrollbar {
  width: 6px;
}
.tier-row::-webkit-scrollbar-thumb,
.deck-list::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

.sortable-ghost {
  opacity: 0.5;
  background: #2a3241;
}
.sortable-drag {
  cursor: grabbing !important;
}
</style>
