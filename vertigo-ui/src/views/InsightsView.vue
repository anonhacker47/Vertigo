<template>
  <div class="flex flex-col w-screen min-h-screen px-8 py-10 bg-base-100">
    <div class="text-3xl font-bold text-white mb-8">Insights</div>
    
    <div class="flex flex-col md:flex-row gap-8 mt-4 w-full">
      <div 
        @click="goToTierList" 
        class="card bg-base-100 shadow-xl border border-gray-700 w-full md:w-96 hover:border-sky-300 transition-colors duration-300 cursor-pointer"
      >
        <div class="card-body">
          <h2 class="card-title text-2xl font-bold flex items-center gap-2 text-gray-50">
            <i class="pi pi-chart-bar text-sky-400"></i> Tier List
          </h2>
          <p class="mt-2 text-gray-400 leading-relaxed">
            Explore your fully curated tier list! See which comics reign supreme and discover hidden gems in your collection.
          </p>
          <div class="card-actions justify-end mt-4">
            <button class="btn btn-sm btn-outline btn-info rounded-full px-4">
              View Tier List <i class="pi pi-arrow-right ml-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToTierList = () => {
  router.push({ name: 'TierList' });
};
</script>

<style scoped>
</style>
