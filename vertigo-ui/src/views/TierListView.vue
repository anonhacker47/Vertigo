<template>
  <div class="flex flex-col w-full bg-base-100 px-4 pb-8 md:px-8">
   <div class="flex flex-col py-4 h-[calc(100dvh-72px)]">
    <div class="flex items-center justify-between gap-4 mb-3 mx-24 shrink-0">
      <div class="flex items-baseline gap-3">
        <h1 class="text-2xl font-bold text-white leading-none">Tier List</h1>
      </div>
      <div class="flex gap-2 shrink-0">
        <button @click="autoRank" class="btn btn-primary btn-sm" title="Rank based on your ratings">
          <i class="pi pi-sparkles"></i><span class="hidden sm:inline">Auto Rank</span>
        </button>
        <button @click="resetTiers" class="btn btn-warning btn-sm" title="Move all to Deck">
          <i class="pi pi-refresh"></i><span class="hidden sm:inline">Reset</span>
        </button>
        <button @click="openExportModal" class="btn btn-success btn-sm" title="Download as Image">
          <i class="pi pi-download"></i><span class="hidden sm:inline">Download</span>
        </button>
      </div>
    </div>

    <div class="bg-base-100 flex flex-col flex-1 min-h-0">
      <div v-if="loading" class="flex flex-1 items-center justify-center">
        <span class="loading loading-ring text-success h-20 w-20"></span>
      </div>

      <div v-else class="flex flex-col gap-2 w-full max-w-7xl mx-auto flex-1 min-h-0">
        <div
          v-for="tier in tiers"
          :key="tier.id"
          class="flex rounded-md overflow-hidden border border-slate-700 bg-[#1a2332] flex-1 min-h-[6rem]"
        >
          <div :class="['w-12 md:w-16 shrink-0 flex items-center justify-center', tier.color]">
            <span class="text-2xl md:text-3xl font-black text-black/80">{{ tier.name }}</span>
          </div>

          <draggable
            v-model="tier.series"
            item-key="id"
            group="series"
            class="tier-row flex-1 min-w-0 flex flex-nowrap items-center gap-2 p-2 bg-base-200/50 overflow-x-auto overflow-y-hidden"
            ghost-class="opacity-50"
            @change="saveState"
          >
            <template #item="{ element: series }">
              <div
                @click="goToSeries(series)"
                class="relative group cursor-pointer shrink-0 h-full max-h-48 aspect-[2/3] rounded overflow-hidden border border-slate-700 hover:border-sky-400 transition-colors"
                :title="`${series.title} (${series.user_rating || 'Unrated'} ⭐)`"
              >
                <img :src="(series.thumbnail as string)" :alt="series.title" crossorigin="anonymous"
                  class="w-full h-full object-cover pointer-events-none" />
                <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-0.5 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <span class="text-[10px] font-bold text-yellow-400">{{ series.user_rating || '-' }} ⭐</span>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>
   </div> 

    <div v-if="!loading" class="mt-4 w-full max-w-7xl mx-auto rounded-md border border-slate-700 bg-base-300 p-4">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h3 class="text-base font-semibold text-white flex items-center gap-2">
          <i class="pi pi-inbox text-gray-400"></i> Deck
          <span class="badge badge-sm badge-primary">{{ filteredDeck.length }}</span>
        </h3>
        <div class="relative w-48 md:w-64">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
          <input v-model="deckSearch" type="text" class="input input-sm input-bordered w-full pl-9 bg-base-100"
            placeholder="Search deck" />
        </div>
      </div>

      <draggable
        v-model="deck"
        item-key="id"
        group="series"
        class="min-h-[10rem] p-3 flex flex-wrap items-center gap-3 rounded border border-dashed border-slate-600 bg-base-200/50"
        ghost-class="opacity-50"
        @change="saveState"
      >
        <template #item="{ element: series }">
          <div
            v-show="matchesDeckFilter(series)"
            @click="goToSeries(series)"
            class="relative group cursor-pointer h-32 aspect-[2/3] shrink-0 rounded overflow-hidden border border-slate-700 hover:border-sky-400 transition-colors"
            :title="`${series.title} (${series.user_rating || 'Unrated'} ⭐)`"
          >
            <img :src="(series.thumbnail as string)" :alt="series.title" crossorigin="anonymous"
              class="w-full h-full object-cover pointer-events-none" />
            <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-0.5 text-center opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-xs font-bold text-yellow-400">{{ series.user_rating || '-' }} ⭐</span>
            </div>
          </div>
        </template>
      </draggable>
    </div>

    <TierListExportModal :show="showExportModal" :initial-title="exportTitle" :busy="exporting"
      @cancel="showExportModal = false" @confirm="exportImage" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
import SeriesService from '@/services/SeriesService';
import { Series } from '@/types/series.types';
import { useRouter } from 'vue-router';
import draggable from 'vuedraggable';
import { useToast } from 'primevue/usetoast';
import TierListExportModal from '@/components/modals/TierListExportModal.vue';
import {
  renderTierListImage, tierListFileName, downloadBlob, isAbortError, type TierListImageTier,
} from '@/utils/tierListImage';

const router = useRouter();
const toast = useToast();
const loading = ref(true);

const deckSearch = ref('');

interface Tier {
  id: string;
  name: string;
  color: string;
  /** Hex of `color` (Tailwind v4 palette), for the canvas export. */
  exportColor: string;
  min: number;
  max: number;
  series: Series[];
}

const tiers = ref<Tier[]>([
  { id: 'S', color: 'bg-red-500', exportColor: '#fb2c36', name: 'S', min: 4.5, max: 5.0, series: [] },
  { id: 'A', color: 'bg-orange-500', exportColor: '#ff6900', name: 'A', min: 4.0, max: 4.49, series: [] },
  { id: 'B', color: 'bg-yellow-400', exportColor: '#fdc700', name: 'B', min: 3.0, max: 3.99, series: [] },
  { id: 'C', color: 'bg-green-500', exportColor: '#00c950', name: 'C', min: 2.0, max: 2.99, series: [] },
  { id: 'D', color: 'bg-blue-500', exportColor: '#2b7fff', name: 'D', min: 0, max: 1.99, series: [] },
]);

const deck = ref<Series[]>([]);

const filteredDeck = computed(() => deck.value.filter(matchesDeckFilter));

const matchesDeckFilter = (series: Series) => {
  if (!deckSearch.value) return true;
  const q = deckSearch.value.toLowerCase();
  return series.title.toLowerCase().includes(q) || 
         (series.author && series.author.toLowerCase().includes(q));
};

const fetchSeries = async () => {
  loading.value = true;
  try {
    const result = await SeriesService.fetchSeries("title", "asc", 2000, 0);
    
    const allSeries = result.seriesList.map(s => ({
      ...s,
      thumbnail: SeriesService.getSeriesImageById(s.id, s.last_updated)
    }));

    loadState(allSeries);

  } catch (error) {
    console.error("Failed to fetch series for tier list:", error);
  } finally {
    loading.value = false;
  }
};

const saveState = () => {
  if (loading.value) return; // Don't save empty states while loading
  
  const state = {
    tiers: tiers.value.map(t => ({
      id: t.id,
      seriesIds: t.series.map(s => s.id)
    })),
    deckSeriesIds: deck.value.map(s => s.id)
  };
  localStorage.setItem('tierListState', JSON.stringify(state));
};

const loadState = (allSeries: Series[]) => {
  const savedStateJson = localStorage.getItem('tierListState');
  if (savedStateJson) {
    try {
      const savedState = JSON.parse(savedStateJson);
      const seriesMap = new Map<number, Series>();
      allSeries.forEach(s => seriesMap.set(s.id, s));
      
      // Load tiers
      savedState.tiers.forEach((savedTier: any) => {
        const tier = tiers.value.find(t => t.id === savedTier.id);
        if (tier) {
          tier.series = savedTier.seriesIds
            .map((id: number) => seriesMap.get(id))
            .filter((s: Series | undefined) => s !== undefined) as Series[];
            
          tier.series.forEach(s => seriesMap.delete(s.id));
        }
      });
      
      let loadedDeck: Series[] = [];
      if (savedState.deckSeriesIds) {
         loadedDeck = savedState.deckSeriesIds
          .map((id: number) => seriesMap.get(id))
          .filter((s: Series | undefined) => s !== undefined) as Series[];
         loadedDeck.forEach(s => seriesMap.delete(s.id));
      }
      
      const remainingSeries = Array.from(seriesMap.values());
      deck.value = [...loadedDeck, ...remainingSeries];

    } catch (e) {
      console.error("Failed to parse saved state", e);
      // Fallback
      resetTiersWithData(allSeries);
    }
  } else {
    // Initial state: all in deck
    resetTiersWithData(allSeries);
  }
};

const resetTiersWithData = (allSeries: Series[]) => {
  tiers.value.forEach(t => t.series = []);
  deck.value = [...allSeries];
  saveState();
};

const resetTiers = () => {
  const allInTiers = tiers.value.flatMap(t => t.series);
  deck.value = [...deck.value, ...allInTiers];
  tiers.value.forEach(t => t.series = []);
  saveState();
};

const autoRank = () => {
  let allSeries = [...deck.value, ...tiers.value.flatMap(t => t.series)];
  
  tiers.value.forEach(t => t.series = []);
  deck.value = [];

  allSeries.forEach(series => {
    if (series.user_rating != null && series.user_rating > 0) {
      const targetTier = tiers.value.find(t => series.user_rating! >= t.min && series.user_rating! <= t.max);
      if (targetTier) {
        targetTier.series.push(series);
      } else {
        deck.value.push(series);
      }
    } else {
      deck.value.push(series);
    }
  });

  tiers.value.forEach(t => {
    t.series.sort((a, b) => (b.user_rating || 0) - (a.user_rating || 0));
  });

  saveState();
};

const EXPORT_TITLE_KEY = 'tierListExportTitle';
const showExportModal = ref(false);
const exporting = ref(false);
const exportTitle = ref(localStorage.getItem(EXPORT_TITLE_KEY) || 'My Tier List');

const coverUrl = (s: Series): string | null =>
  typeof s.thumbnail === 'string' && s.thumbnail && s.thumbnail !== 'noimage' ? s.thumbnail : null;

const exportTiers = computed<TierListImageTier[]>(() =>
  tiers.value.map(t => ({ name: t.name, color: t.exportColor, covers: t.series.map(coverUrl) }))
);

const openExportModal = () => {
  if (!loading.value) showExportModal.value = true;
};

let exportAbort: AbortController | null = null;
onBeforeUnmount(() => exportAbort?.abort());

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

const goToSeries = (series: Series) => {
  router.push({ name: 'SeriesDetail', params: { Id: series.id.toString(), Link: series.slug } });
};

onMounted(fetchSeries);
</script>

<style scoped>
.tier-row {
  scrollbar-width: thin;
  scrollbar-color: #475569 transparent;
}
.tier-row::-webkit-scrollbar {
  height: 6px;
}
.tier-row::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

/* Disable selection while dragging */
.sortable-ghost {
  opacity: 0.5;
  background: #2a3241;
}
.sortable-drag {
  cursor: grabbing !important;
}
</style>
