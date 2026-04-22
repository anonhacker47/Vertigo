<template>
  <div class="flex flex-col w-screen min-h-screen px-4 py-8 md:px-8 md:py-10 bg-base-100">
    <div class="text-3xl font-bold text-white mb-2">Series Tier List</div>
    <div class="text-sm text-gray-400 mb-8">Rankings based on your personal ratings for series you have read.</div>
    
    <div v-if="loading" class="flex justify-center items-center py-20">
      <span class="loading-ring text-success h-20 w-20 loading"></span>
    </div>

    <div v-else class="flex flex-col gap-4 w-full">
      <div 
        v-for="tier in tiers" 
        :key="tier.id" 
        class="flex flex-col md:flex-row bg-[#1a2332] rounded-lg shadow-xl overflow-hidden border border-slate-700"
      >
        <!-- Tier Label -->
        <div 
          :class="['w-full md:w-28 shrink-0 flex items-center justify-center p-4', tier.color]"
        >
          <span class="text-5xl font-black text-black opacity-80 tracking-tighter drop-shadow-sm">{{ tier.name }}</span>
        </div>

        <!-- Tier Content -->
        <div class="flex-1 p-4 bg-base-200/50 min-h-[10rem] flex flex-wrap gap-4 items-center">
          <template v-if="getSeriesForTier(tier).length > 0">
            <div 
              v-for="series in getSeriesForTier(tier)" 
              :key="series.id"
              @click="goToSeries(series)"
              class="relative group cursor-pointer w-24 h-36 shrink-0 rounded-md overflow-hidden shadow-md hover:shadow-xl hover:scale-105 transition-all duration-300 border border-slate-700 hover:border-sky-400"
              :title="`${series.title} (${series.user_rating} ⭐)`"
            >
               <img 
                 :src="(series.thumbnail as string)" 
                 :alt="series.title"
                 class="w-full h-full object-cover"
               />
               <!-- Rating Badge -->
               <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-1 text-center backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
                 <span class="text-xs font-bold text-yellow-400">{{ series.user_rating }} ⭐</span>
               </div>
            </div>
          </template>
          <div v-else class="w-full text-center text-gray-500 italic py-4">
            No series in this tier yet.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import SeriesService from '@/services/SeriesService';
import { Series } from '@/types/series.types';
import { useRouter } from 'vue-router';

const router = useRouter();
const seriesList = ref<Series[]>([]);
const loading = ref(true);

const fetchSeries = async () => {
  loading.value = true;
  try {
    const result = await SeriesService.fetchSeries("user_rating", "desc", 2000, 0);
    
    // Filter to read and rated series
    seriesList.value = result.seriesList
      .filter((s) => s.read_count > 0 && s.user_rating != null && s.user_rating > 0)
      .map(s => ({
        ...s,
        thumbnail: SeriesService.getSeriesImageById(s.id, s.last_updated)
      }));
  } catch (error) {
    console.error("Failed to fetch series for tier list:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchSeries);

// Standard Tier Definitions
const tiers = [
  { id: 'S', color: 'bg-red-500', name: 'S', min: 4.5, max: 5.0 },
  { id: 'A', color: 'bg-orange-500', name: 'A', min: 4.0, max: 4.49 },
  { id: 'B', color: 'bg-yellow-400', name: 'B', min: 3.0, max: 3.99 },
  { id: 'C', color: 'bg-green-500', name: 'C', min: 2.0, max: 2.99 },
  { id: 'D', color: 'bg-blue-500', name: 'D', min: 0, max: 1.99 },
];

const getSeriesForTier = (tier: typeof tiers[0]) => {
  return seriesList.value
    .filter(s => s.user_rating >= tier.min && s.user_rating <= tier.max)
    .sort((a, b) => b.user_rating - a.user_rating);
};

const goToSeries = (series: Series) => {
  router.push({ name: 'SeriesDetail', params: { Id: series.id.toString(), Link: series.slug } });
};
</script>

<style scoped>
</style>
