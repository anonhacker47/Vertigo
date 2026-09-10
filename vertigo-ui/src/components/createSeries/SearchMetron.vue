  <template>
    <div class="rounded-2xl border border-base-300 bg-base-100 p-4 shadow-sm">
      <div class="mb-2 flex items-center gap-2">
        <i class="pi pi-search text-lg"></i>
        <h3 class="text-sm font-semibold text-base-content">
          Search Comics (MetronDB)
        </h3>
      </div>

      <div class="flex gap-2">
        <InputText v-model="query" placeholder="Eg: Watchmen" class="w-full" @keyup.enter="search" />
        <Button icon="pi pi-search" label="Search" iconPos="left" :loading="searchLoading" class="px-6"
          severity="primary" @click="search" />
        <Button icon="pi pi-times" label="Clear" class="px-4" outlined @click="clear" />
      </div>
    </div>

    <Dialog v-model:visible="showModal" modal header="Select Series from Metron" class="w-[95vw] md:w-240">
      <div v-if="!seriesDetail && !detailLoading" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="item in results" :key="item.metron_id"
          class="rounded-xl border border-base-300 p-3 cursor-pointer select-none transition hover:border-primary"
          @click="fetchSeriesDetail(item.metron_id)">
          <h4 class="font-semibold leading-tight">{{ item.name }}</h4>
          <p class="text-xs opacity-70">Year began: {{ item.year_began }}</p>
          <p class="mt-1 text-xs opacity-70">{{ item.issue_count }} issues • Vol. {{ item.volume }}</p>
        </div>
      </div>

      <div v-if="detailLoading" class="flex items-center justify-center py-24">
        <ProgressSpinner style="width:80px;height:80px" strokeWidth="4" animationDuration=".8s" />
      </div>

      <div v-if="seriesDetail" class="flex flex-col gap-4">
        <Button label="Back" icon="pi pi-arrow-left" class="w-fit" outlined :disabled="entitiesLoading || selecting"
          @click="seriesDetail = null; seriesEntities = null" />

        <div class="flex flex-col md:flex-row gap-4">
          <img :src="seriesDetail.image_first_issue" alt="First Issue"
            class="w-48 max-h-96 md:w-64 rounded-lg shadow" />

          <div class="flex flex-col gap-2">
            <h3 class="text-xl font-bold">{{ seriesDetail.name }}</h3>
            <p class="text-sm opacity-70">{{ seriesDetail.publisher.name }}</p>
            <p class="text-sm opacity-70">Volume: {{ seriesDetail.volume }} • Issues: {{ seriesDetail.issue_count }}</p>
            <p class="text-sm opacity-70">Years: {{ seriesDetail.year_began }} – {{ seriesDetail.year_end || 'Present'
              }}
            </p>
            <p class="text-sm opacity-70">Status: {{ seriesDetail.status }}</p>
            <p class="text-sm opacity-70">
              Genres:
              {{seriesDetail.genres.map(genre => genre.name).join(', ')}}
            </p>
            <p class="text-sm mt-2">{{ seriesDetail.desc }}</p>

            <div class="flex flex-row flex-wrap gap-3">
              <Button as="a" :href="seriesDetail.metron_url" target="_blank" rel="noopener noreferrer"
                label="View on Metron" icon="pi pi-external-link" severity="info" class="w-fit" />
              <Button v-if="!seriesEntities" label="Load creators & characters" icon="pi pi-users" class="w-fit"
                severity="secondary" :loading="entitiesLoading" :disabled="selecting"
                @click="fetchSeriesEntities(seriesDetail.metron_id)" />
            </div>

            <EntityPreview v-if="seriesEntities" class="mt-4" :creators="seriesEntities.creators"
              :characters="seriesEntities.characters" creators-label="Creators" source="Metron"
              :note="entitiesNote" />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Close" severity="secondary" outlined @click="closeModal" />
        <Button v-if="seriesDetail" :label="`Select ${seriesDetail.name}`" severity="primary" :loading="selecting"
          :disabled="entitiesLoading" @click="selectSeries" />
      </template>
    </Dialog>
  </template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import MokkariService from '@/services/MetronService'
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

// "Load creators & characters" button: spins that button only.
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

  // Footer "Select" button: fetch quietly if needed, spinning that button only.
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
.p-button {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
</style>
