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
        <Button label="Back" icon="pi pi-arrow-left" class="w-fit" outlined
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

            <div class="flex flex-row gap-4">

              <Button as="a" :href="seriesDetail.metron_url" target="_blank" rel="noopener noreferrer"
                label="View on Metron" icon="pi pi-external-link" severity="info" class="w-fit" />
              <Button label="Load Creators & Characters" icon="pi pi-users" class="w-fit" severity="secondary"
                :loading="entitiesLoading" @click="fetchSeriesEntities(seriesDetail.metron_id)" />
            </div>

            <div v-if="entitiesLoading" class="flex justify-center py-8">
              <ProgressSpinner style="width:60px;height:60px" strokeWidth="4" />
            </div>

            <div v-if="seriesEntities" class="mt-6 grid gap-6 md:grid-cols-2">
              <div class="rounded-xl border border-base-300 p-4">
                <h4 class="mb-2 text-sm font-semibold">
                  Creators ({{ seriesEntities.total_creators }})
                </h4>

                <ul class="space-y-1 text-sm">
                  <li v-for="creator in seriesEntities.creators" :key="creator">
                    • {{ creator.value }}
                  </li>
                </ul>
              </div>

              <div class="rounded-xl border border-base-300 p-4">
                <h4 class="mb-2 text-sm font-semibold">
                  Characters ({{ seriesEntities.total_characters }})
                </h4>

                <ul class="space-y-1 text-sm">
                  <li v-for="character in seriesEntities.characters" :key="char">
                    • {{ character.value }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Close" severity="secondary" outlined @click="closeModal" />
        <Button v-if="seriesDetail" :label="`Select ${seriesDetail.name}`" severity="primary" @click="selectSeries" />
      </template>
    </Dialog>
  </template>

<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import MokkariService from '@/services/MetronService'
import ProgressSpinner from 'primevue/progressspinner'

const emit = defineEmits(['select'])

const query = ref('')
const results = ref([])
const searchLoading = ref(false)
const detailLoading = ref(false)
const entitiesLoading = ref(false)
const showModal = ref(false)

const seriesDetail = ref<any>(null)
const seriesEntities = ref<any | null>(null)

async function search() {
  if (query.value.trim().length < 3) return

  searchLoading.value = true
  results.value = []
  seriesDetail.value = null

  try {
    const res = await MokkariService.getSeriesByQuery(query.value)
    results.value = res.data.items || []
    if (results.value.length) showModal.value = true
  } catch {
    results.value = []
  } finally {
    searchLoading.value = false
  }
}

async function fetchSeriesDetail(metron_id: number) {
  detailLoading.value = true
  try {
    const res = await MokkariService.getSeriesDetail(metron_id)
    seriesDetail.value = res.data
  } catch {
    seriesDetail.value = null
  } finally {
    detailLoading.value = false
  }
}

async function fetchSeriesEntities(metron_id: number) {
  entitiesLoading.value = true
  seriesEntities.value = null

  try {
    const res = await MokkariService.getSeriesEntities(metron_id)
    seriesEntities.value = res.data
  } catch {
    seriesEntities.value = null
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

  if (!seriesEntities.value) {
    try {
      entitiesLoading.value = true
      const res = await MokkariService.getSeriesEntities(seriesDetail.value.metron_id)
      seriesEntities.value = res.data
    } catch {
      seriesEntities.value = null
    } finally {
      entitiesLoading.value = false
    }
  }

  emit('select', seriesDetail.value, seriesEntities.value)
  closeModal()
}
</script>

<style scoped>
.p-button {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
</style>
