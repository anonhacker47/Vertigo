<template>
  <div class="flex min-w-0 flex-1 items-center gap-2">
    <div class="relative min-w-0 flex-1">
      <i class="pi pi-search pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" style="font-size: 14px"></i>
      <input
        v-model="query"
        type="text"
        class="fm-input fm-input--bare pl-9 pr-9"
        placeholder="Search Metron for a comic"
        aria-label="Search Metron for a comic"
        autocomplete="off"
        @keydown.enter.prevent="search"
      />
      <button
        v-if="query"
        type="button"
        class="fm-iconbtn fm-iconbtn--sm absolute right-1.5 top-1/2 -translate-y-1/2 border-0"
        aria-label="Clear search"
        @click="clear"
      >
        <i class="pi pi-times" style="font-size: 11px"></i>
      </button>
    </div>
    <button type="button" class="fm-btn fm-btn--primary fm-btn--sm" :disabled="searchLoading || query.trim().length < 3" @click="search">
      <i v-if="searchLoading" class="pi pi-spin pi-spinner" style="font-size: 12px"></i>
      <span>{{ searchLoading ? "Searching" : "Search" }}</span>
    </button>

    <Dialog v-model:visible="showModal" modal header="Choose a series" class="w-[95vw] md:w-240">
      <ul v-if="!seriesDetail && !detailLoading" class="grid gap-2 sm:grid-cols-2">
        <li v-for="item in results" :key="item.metron_id">
          <button type="button" class="result" @click="fetchSeriesDetail(item.metron_id)">
            <span class="block text-[15px] font-extrabold leading-tight text-white">{{ item.name }}</span>
            <span class="mt-1 block text-[13px] font-semibold text-slate-400">
              Began {{ item.year_began }}, {{ item.issue_count }} issues, volume {{ item.volume }}
            </span>
          </button>
        </li>
      </ul>

      <div v-if="detailLoading" class="flex items-center justify-center py-24">
        <ProgressSpinner style="width: 64px; height: 64px" strokeWidth="4" animationDuration=".8s" />
      </div>

      <div v-if="seriesDetail" class="flex flex-col gap-4">
        <div>
          <Button label="Back to results" icon="pi pi-arrow-left" size="small" text :disabled="entitiesLoading || selecting" @click="seriesDetail = null; seriesEntities = null" />
        </div>

        <div class="flex flex-col gap-5 md:flex-row">
          <div class="w-40 shrink-0 md:w-52">
            <CoverImage :src="seriesDetail.image_first_issue" :title="seriesDetail.name" alt="First issue cover" :interactive="false" />
          </div>

          <div class="flex min-w-0 flex-col gap-2">
            <h3 class="text-xl font-extrabold leading-tight text-white">{{ seriesDetail.name }}</h3>
            <p class="text-sm font-semibold text-slate-400">{{ seriesDetail.publisher?.value }}</p>
            <dl class="meta mt-1 grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-1 text-sm">
              <dt>Volume</dt><dd>{{ seriesDetail.volume }}</dd>
              <dt>Issues</dt><dd>{{ seriesDetail.issue_count }}</dd>
              <dt>Years</dt><dd>{{ seriesDetail.year_began }} to {{ seriesDetail.year_end || "present" }}</dd>
              <dt>Status</dt><dd>{{ seriesDetail.status }}</dd>
              <dt>Genres</dt><dd>{{ genreList || "none listed" }}</dd>
            </dl>
            <p class="mt-1 text-sm text-slate-300">{{ seriesDetail.desc }}</p>

            <div class="mt-1 flex flex-row flex-wrap gap-3">
              <Button as="a" :href="seriesDetail.metron_url" target="_blank" rel="noopener noreferrer"
                label="View on Metron" icon="pi pi-external-link" size="small" severity="secondary" outlined />
              <Button v-if="!seriesEntities" label="Load creators and characters" icon="pi pi-users" size="small"
                severity="secondary" :loading="entitiesLoading" :disabled="selecting"
                @click="fetchSeriesEntities(seriesDetail.metron_id)" />
            </div>

            <EntityPreview v-if="seriesEntities" class="mt-3" :creators="seriesEntities.creators"
              :characters="seriesEntities.characters" creators-label="Creators" source="Metron" :note="entitiesNote" />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Close" severity="secondary" outlined @click="closeModal" />
        <Button v-if="seriesDetail" :label="`Use ${seriesDetail.name}`" :loading="selecting" :disabled="entitiesLoading" @click="selectSeries" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import MokkariService from '@/services/MetronService'
import CoverImage from '@/components/common/CoverImage.vue'
import EntityPreview from '@/components/createSeries/EntityPreview.vue'
import { useToast } from 'primevue/usetoast'

const emit = defineEmits(['select'])
const toast = useToast()

const query = ref('')
const results = ref([])
const searchLoading = ref(false)
const detailLoading = ref(false)
const entitiesLoading = ref(false)
const selecting = ref(false)
const showModal = ref(false)

const seriesDetail = ref<any>(null)
const seriesEntities = ref<any | null>(null)

const genreList = computed(() => (seriesDetail.value?.genres || []).map((genre: any) => genre.value).join(', '))

const entitiesNote = computed(() => {
  const e = seriesEntities.value
  if (!e) return ''
  const total = e.total_issues ?? 0
  const sampled = e.sampled_issues ?? 0
  if (e.partial) {
    const wait = e.retry_after ? ` Try again in ${e.retry_after}s to read more.` : ' Try again shortly to read more.'
    return `Metron's rate limit stopped the scan after ${sampled} of ${total} issues.` + wait
  }
  if (total > sampled) return `From the first ${sampled} of ${total} issues.`
  return ''
})

function notifyMetronError(error: any, summary: string) {
  const data = error?.response?.data
  let detail: string
  if (data?.error === 'rate_limited') {
    const wait = data.retry_after ? ` Try again in ${data.retry_after}s.` : ' Try again in a minute.'
    detail = 'Metron is rate limiting requests.' + wait
  } else {
    detail = data?.message || data?.description || 'Could not reach Metron. Please try again.'
  }
  console.error(summary, data || error)
  toast.add({ severity: 'error', summary, detail, life: 5000 })
}

async function search() {
  if (query.value.trim().length < 3) return

  searchLoading.value = true
  results.value = []
  seriesDetail.value = null

  try {
    const res = await MokkariService.getSeriesByQuery(query.value)
    results.value = res.data.items || []
    if (results.value.length) showModal.value = true
    else toast.add({ severity: 'info', summary: 'No matches', detail: `Metron has nothing for "${query.value.trim()}".`, life: 3000 })
  } catch (error) {
    results.value = []
    notifyMetronError(error, 'Comic search failed')
  } finally {
    searchLoading.value = false
  }
}

async function fetchSeriesDetail(metron_id: number) {
  detailLoading.value = true
  try {
    const res = await MokkariService.getSeriesDetail(metron_id)
    seriesDetail.value = res.data
  } catch (error) {
    seriesDetail.value = null
    notifyMetronError(error, 'Could not load series details')
  } finally {
    detailLoading.value = false
  }
}

async function loadEntities(metron_id: number) {
  const res = await MokkariService.getSeriesEntities(metron_id)
  return res.data
}

// "Load creators and characters" button: spins that button only.
async function fetchSeriesEntities(metron_id: number) {
  entitiesLoading.value = true
  seriesEntities.value = null

  try {
    seriesEntities.value = await loadEntities(metron_id)
  } catch (error) {
    seriesEntities.value = null
    notifyMetronError(error, 'Could not load creators and characters')
  } finally {
    entitiesLoading.value = false
  }
}

function clear() {
  query.value = ''
  results.value = []
  seriesDetail.value = null
  seriesEntities.value = null
  showModal.value = false
}

function closeModal() {
  showModal.value = false
  seriesDetail.value = null
  seriesEntities.value = null
}

async function selectSeries() {
  if (!seriesDetail.value) return

  // Footer button: fetch quietly if needed, spinning that button only.
  if (!seriesEntities.value) {
    selecting.value = true
    try {
      seriesEntities.value = await loadEntities(seriesDetail.value.metron_id)
    } catch (error) {
      seriesEntities.value = null
      notifyMetronError(error, 'Could not load creators and characters')
    } finally {
      selecting.value = false
    }
  }
  const metronIssues = seriesEntities.value?.issues || []
  emit('select', seriesDetail.value, seriesEntities.value, metronIssues)
  closeModal()
}
</script>

<style scoped>
.result {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0b1220;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.12s ease;
}
.result:hover { border-color: #38bdf8; }
.result:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
.meta dt { font-weight: 700; color: #64748b; }
.meta dd { color: #cbd5e1; }
</style>
