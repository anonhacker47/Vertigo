<template>
  <div class="flex flex-col w-full min-h-screen px-4 py-8 md:px-8 md:py-10 bg-base-100" ref="tierListContainer">
    <!-- Top Control Bar -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white px-2 py-1">Series Tier List</h1>
        <div class="text-sm text-gray-400 mt-1 px-2">Drag and drop to rank your series, or use Auto Rank.</div>
      </div>
      
      <div class="flex gap-2 flex-wrap">
        <button @click="autoRank" class="btn btn-primary btn-sm md:btn-md" title="Rank based on your ratings">
          <i class="pi pi-sparkles"></i> Auto Rank
        </button>
        <button @click="resetTiers" class="btn btn-warning btn-sm md:btn-md" title="Move all to Deck">
          <i class="pi pi-refresh"></i> Reset
        </button>
        <button @click="downloadImage" class="btn btn-success btn-sm md:btn-md" title="Download as Image">
          <i class="pi pi-download"></i> Download
        </button>
      </div>
    </div>

    <!-- Tier List Wrapper for Image Export -->
    <div ref="tierListExportArea" class="bg-base-100 pb-12">
      <!-- Title on export -->
      <div v-if="isExporting" class="text-4xl font-bold text-white mb-8 text-center pt-8">
        {{ exportTitle }}
      </div>

      <div v-if="loading" class="flex justify-center items-center py-20">
        <span class="loading-ring text-success h-20 w-20 loading"></span>
      </div>

      <div v-else class="flex flex-col gap-4 w-full max-w-7xl mx-auto">
        <div 
          v-for="(tier, index) in tiers" 
          :key="tier.id" 
          class="flex flex-col md:flex-row bg-[#1a2332] rounded-lg shadow-xl overflow-hidden border border-slate-700"
        >
          <!-- Tier Label -->
          <div 
            :class="['w-full md:w-28 shrink-0 flex items-center justify-center p-4', tier.color]"
          >
            <span class="text-5xl font-black text-black opacity-80 tracking-tighter drop-shadow-sm">{{ tier.name }}</span>
          </div>

          <!-- Tier Content (Draggable) -->
          <draggable
            v-model="tier.series"
            item-key="id"
            group="series"
            class="flex-1 p-4 bg-base-200/50 min-h-[10rem] flex flex-wrap gap-4 items-center"
            ghost-class="opacity-50"
            @change="saveState"
          >
            <template #item="{ element: series }">
              <div 
                @click="goToSeries(series)"
                class="relative group cursor-pointer w-24 h-36 shrink-0 rounded-md overflow-hidden shadow-md hover:shadow-xl hover:scale-105 transition-all duration-300 border border-slate-700 hover:border-sky-400"
                :title="`${series.title} (${series.user_rating || 'Unrated'} ⭐)`"
              >
                 <img 
                   :src="(series.thumbnail as string)" 
                   :alt="series.title"
                   class="w-full h-full object-cover pointer-events-none"
                 />
                 <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-1 text-center backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
                   <span class="text-xs font-bold text-yellow-400">{{ series.user_rating || '-' }} ⭐</span>
                 </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div> <!-- End Export Area -->

    <!-- Deck Area (Unranked) -->
    <div v-if="!loading" class="mt-12 bg-base-300 rounded-xl p-6 border border-slate-700 shadow-2xl max-w-7xl mx-auto w-full">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-4">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
          <i class="pi pi-inbox"></i> Deck (Unranked)
          <span class="badge badge-primary">{{ filteredDeck.length }}</span>
        </h3>
        
        <!-- Filter/Search -->
        <div class="flex gap-2 w-full md:w-auto">
          <div class="relative w-full md:w-64">
            <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
            <input 
              v-model="deckSearch" 
              type="text" 
              class="input input-sm input-bordered w-full pl-9 bg-base-100" 
              placeholder="Search in deck..." 
            />
          </div>
        </div>
      </div>

      <draggable
        v-model="deck"
        item-key="id"
        group="series"
        class="bg-base-200/50 min-h-[12rem] rounded-lg p-4 border border-slate-600 border-dashed flex flex-wrap gap-4 items-center"
        ghost-class="opacity-50"
        @change="saveState"
      >
        <template #item="{ element: series }">
          <div 
            v-show="matchesDeckFilter(series)"
            @click="goToSeries(series)"
            class="relative group cursor-pointer w-24 h-36 shrink-0 rounded-md overflow-hidden shadow-md hover:shadow-xl hover:scale-105 transition-all duration-300 border border-slate-700 hover:border-sky-400"
            :title="`${series.title} (${series.user_rating || 'Unrated'} ⭐)`"
          >
             <img 
               :src="(series.thumbnail as string)" 
               :alt="series.title"
               class="w-full h-full object-cover pointer-events-none"
             />
             <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-1 text-center backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
               <span class="text-xs font-bold text-yellow-400">{{ series.user_rating || '-' }} ⭐</span>
             </div>
          </div>
        </template>
      </draggable>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import SeriesService from '@/services/SeriesService';
import { Series } from '@/types/series.types';
import { useRouter } from 'vue-router';
import draggable from 'vuedraggable';
import { toPng } from 'html-to-image';

const router = useRouter();
const loading = ref(true);

const tierListTitle = ref('Series Tier List');
const exportTitle = ref('Series Tier List');
const deckSearch = ref('');
const tierListExportArea = ref<HTMLElement | null>(null);
const isExporting = ref(false);

// watch(tierListTitle, (newVal) => {
//   localStorage.setItem('tierListTitle', newVal);
// });

interface Tier {
  id: string;
  name: string;
  color: string;
  min: number;
  max: number;
  series: Series[];
}

const tiers = ref<Tier[]>([
  { id: 'S', color: 'bg-red-500', name: 'S', min: 4.5, max: 5.0, series: [] },
  { id: 'A', color: 'bg-orange-500', name: 'A', min: 4.0, max: 4.49, series: [] },
  { id: 'B', color: 'bg-yellow-400', name: 'B', min: 3.0, max: 3.99, series: [] },
  { id: 'C', color: 'bg-green-500', name: 'C', min: 2.0, max: 2.99, series: [] },
  { id: 'D', color: 'bg-blue-500', name: 'D', min: 0, max: 1.99, series: [] },
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
    
    // We want to load ALL series into the pool initially.
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
            
          // Remove from map to find remainders
          tier.series.forEach(s => seriesMap.delete(s.id));
        }
      });
      
      // Load deck with saved order, plus any new series not in state
      let loadedDeck: Series[] = [];
      if (savedState.deckSeriesIds) {
         loadedDeck = savedState.deckSeriesIds
          .map((id: number) => seriesMap.get(id))
          .filter((s: Series | undefined) => s !== undefined) as Series[];
         loadedDeck.forEach(s => seriesMap.delete(s.id));
      }
      
      // Any remaining series that weren't in state (e.g. newly added to DB)
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
  // Move everything back to deck
  const allInTiers = tiers.value.flatMap(t => t.series);
  deck.value = [...deck.value, ...allInTiers];
  tiers.value.forEach(t => t.series = []);
  saveState();
};

const autoRank = () => {
  // Collect all series from tiers and deck
  let allSeries = [...deck.value, ...tiers.value.flatMap(t => t.series)];
  
  tiers.value.forEach(t => t.series = []);
  deck.value = [];

  allSeries.forEach(series => {
    // Only rank if they have a rating
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

  // Sort tiers by rating descending
  tiers.value.forEach(t => {
    t.series.sort((a, b) => (b.user_rating || 0) - (a.user_rating || 0));
  });

  saveState();
};

const downloadImage = async () => {
  if (!tierListExportArea.value) return;
  
  const title = window.prompt("Enter a title for your Tier List:", exportTitle.value || "My Series Tier List");
  if (title === null) return; // User cancelled
  
  exportTitle.value = title;
  
  try {
    isExporting.value = true;
    
    // Wait for Vue to update the DOM
    await new Promise(resolve => setTimeout(resolve, 200));

    const dataUrl = await toPng(tierListExportArea.value, { 
      backgroundColor: '#0f172a',
      style: {
        padding: '40px', // Increased padding to prevent cutting
        margin: '0'
      },
      // Ensure we capture the full height
      cacheBust: true,
    });
    
    const link = document.createElement('a');
    link.download = `${exportTitle.value.replace(/\s+/g, '_')}.png`;
    link.href = dataUrl;
    link.click();

  } catch (error) {
    console.error('Failed to generate image', error);
    alert("Failed to generate image. Please try again.");
  } finally {
    isExporting.value = false;
  }
};

const goToSeries = (series: Series) => {
  router.push({ name: 'SeriesDetail', params: { Id: series.id.toString(), Link: series.slug } });
};

onMounted(fetchSeries);
</script>

<style scoped>
/* Disable selection while dragging */
.sortable-ghost {
  opacity: 0.5;
  background: #2a3241;
}
.sortable-drag {
  cursor: grabbing !important;
}
</style>
