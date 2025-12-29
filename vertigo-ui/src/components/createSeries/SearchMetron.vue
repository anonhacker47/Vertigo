<template>
  <div class="mb-2 rounded-2xl border border-base-300 bg-base-100 p-4 shadow-sm">
    <div class="mb-2 flex items-center gap-2">
      <i class="pi pi-search text-lg"></i>
      <h3 class="text-sm font-semibold text-base-content">
        Search Metron (optional)
      </h3>
    </div>

    <div class="flex gap-2">
      <InputText v-model="query" placeholder="Eg: Watchmen" class="w-full" @keyup.enter="search" />

      <Button icon="pi pi-search" label="Search" :loading="loading" class="px-6" severity="primary" @click="search" />
      <Button icon="pi pi-times" class="px-4" outlined @click="clear" />
    </div>
  </div>

  <!-- Results Modal -->
  <Dialog v-model:visible="showModal" modal header="Select Series from Metron" class="w-[95vw] md:w-[60rem]">
    <div v-if="!seriesDetail" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="item in results" :key="item.series_id"
          class="rounded-xl border border-base-300 p-3 cursor-pointer select-none border-slate-400 transition hover:border-primary"
          @click="fetchSeriesDetail(item.series_id)">
        <h4 class="font-semibold leading-tight">{{ item.name }}</h4>
        <p class="text-xs opacity-70">Year began: {{ item.year_began }}</p>
        <p class="mt-1 text-xs opacity-70">{{ item.issue_count }} issues • Vol. {{ item.volume }}</p>
      </div>
    </div>

    <!-- Series Detail View -->
    <div v-if="seriesDetail" class="flex flex-col gap-4">
      <Button label="Back" icon="pi pi-arrow-left" class="w-fit" outlined @click="seriesDetail = null" />

      <div class="flex flex-col md:flex-row gap-4">
        <img :src="seriesDetail.image_first_issue" alt="First Issue" class="w-48 md:w-64 rounded-lg shadow" />

        <div class="flex flex-col gap-2">
          <h3 class="text-xl font-bold">{{ seriesDetail.name }}</h3>
          <p class="text-sm opacity-70">{{ seriesDetail.publisher }} • {{ seriesDetail.imprint || 'N/A' }}</p>
          <p class="text-sm opacity-70">Volume: {{ seriesDetail.volume }} • Issues: {{ seriesDetail.issue_count }}</p>
          <p class="text-sm opacity-70">Years: {{ seriesDetail.year_began }} – {{ seriesDetail.year_end || 'Present' }}</p>
          <p class="text-sm opacity-70">Status: {{ seriesDetail.status }}</p>
          <p class="text-sm">Genres: {{ seriesDetail.genres.join(', ') }}</p>
          <p class="text-sm mt-2">{{ seriesDetail.desc }}</p>
          <a :href="seriesDetail.resource_url" target="_blank" class="text-primary mt-2 underline">View on Metron</a>
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Close" severity="secondary" outlined @click="closeModal" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import MokkariService from '@/services/MokkariService'

const emit = defineEmits(['select'])

const query = ref('')
const results = ref([])
const loading = ref(false)
const showModal = ref(false)
const seriesDetail = ref<any>(null)

async function search() {
  if (query.value.trim().length < 3) return

  loading.value = true
  results.value = []
  seriesDetail.value = null

  try {
    const res = await MokkariService.getSeriesbyQuery(query.value)
    results.value = res.data.items || []
    if (results.value.length) showModal.value = true
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}

async function fetchSeriesDetail(id: number) {
  loading.value = true
  try {
    const res = await MokkariService.getSeriesDetail(id)
    seriesDetail.value = res.data
  } catch {
    seriesDetail.value = null
  } finally {
    loading.value = false
  }
}

function clear() {
  query.value = ''
  results.value = []
  seriesDetail.value = null
  showModal.value = false
}

function closeModal() {
  showModal.value = false
  seriesDetail.value = null
}
</script>
