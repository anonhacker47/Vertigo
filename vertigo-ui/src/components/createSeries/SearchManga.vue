<template>
  <div class="flex min-w-0 flex-1 items-center gap-2">
    <div class="relative min-w-0 flex-1">
      <i class="pi pi-search pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" style="font-size: 14px"></i>
      <input
        v-model="query"
        type="text"
        class="fm-input fm-input--bare pl-9 pr-9"
        placeholder="Search MyAnimeList for a manga"
        aria-label="Search MyAnimeList for a manga"
        autocomplete="off"
        @keydown.enter.prevent="search"
      />
      <span v-if="query" class="absolute right-1 top-1/2 -translate-y-1/2">
        <Button icon="pi pi-times" text rounded size="small" severity="secondary" aria-label="Clear search" @click="clear" />
      </span>
    </div>
    <Button :label="searchLoading ? 'Searching' : 'Search'" icon="pi pi-search" size="small" :loading="searchLoading"
      :disabled="query.trim().length < 3" @click="search" />

    <Dialog v-model:visible="showModal" modal header="Choose a manga" class="w-[95vw] md:w-240">
      <ul v-if="!mangaDetail && !detailLoading" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <li v-for="item in results" :key="item.mal_id">
          <button type="button" class="tile" @click="fetchMangaDetail(item.mal_id)">
            <CoverImage :src="item.image_url" :title="item.name" :interactive="false" depth="sm" />
            <span class="mt-2 line-clamp-2 block text-sm font-extrabold leading-tight text-white">{{ item.name }}</span>
            <span class="mt-1 block text-xs font-semibold text-slate-400">
              {{ item.year_began || "Year unknown" }}, {{ item.chapter_count || "?" }} chapters, {{ item.volume_count || "?" }} volumes
            </span>
          </button>
        </li>
      </ul>

      <div v-if="detailLoading" class="flex items-center justify-center py-24">
        <ProgressSpinner style="width: 64px; height: 64px" strokeWidth="4" animationDuration=".8s" />
      </div>

      <div v-if="mangaDetail" class="flex flex-col gap-4">
        <div>
          <Button label="Back to results" icon="pi pi-arrow-left" size="small" text :disabled="entitiesLoading || selecting" @click="mangaDetail = null; mangaEntities = null" />
        </div>

        <div class="flex flex-col gap-5 md:flex-row">
          <div class="w-40 shrink-0 md:w-52">
            <CoverImage :src="mangaDetail.image_url" :title="mangaDetail.name" alt="Cover" :interactive="false" />
          </div>

          <div class="flex min-w-0 flex-col gap-2">
            <h3 class="text-xl font-extrabold leading-tight text-white">{{ mangaDetail.name }}</h3>
            <dl class="meta mt-1 grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-1 text-sm">
              <dt>Chapters</dt><dd>{{ mangaDetail.chapter_count || "?" }}</dd>
              <dt>Volumes</dt><dd>{{ mangaDetail.volume_count || "?" }}</dd>
              <dt>Year</dt><dd>{{ mangaDetail.year_began || "unknown" }}</dd>
              <dt>Status</dt><dd>{{ mangaDetail.status }}</dd>
              <dt>Genres</dt><dd>{{ genreList || "none listed" }}</dd>
            </dl>
            <p class="mt-1 text-sm text-slate-300">{{ mangaDetail.desc }}</p>

            <div class="mt-1 flex flex-row flex-wrap gap-3">
              <Button as="a" :href="mangaDetail.mal_url" target="_blank" rel="noopener noreferrer"
                label="View on MyAnimeList" icon="pi pi-external-link" size="small" severity="secondary" outlined />
              <Button v-if="!mangaEntities" label="Load authors and characters" icon="pi pi-users" size="small"
                severity="secondary" :loading="entitiesLoading" :disabled="selecting"
                @click="fetchMangaEntities(mangaDetail.mal_id)" />
            </div>

            <EntityPreview v-if="mangaEntities" class="mt-3" :creators="mangaEntities.creators"
              :characters="mangaEntities.characters" creators-label="Authors" source="MyAnimeList" />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Close" severity="secondary" outlined @click="closeModal" />
        <Button v-if="mangaDetail" :label="`Use ${mangaDetail.name}`" :loading="selecting" :disabled="entitiesLoading" @click="selectManga" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'
import TenraiService from '@/services/TenraiService'
import CoverImage from '@/components/common/CoverImage.vue'
import EntityPreview from '@/components/createSeries/EntityPreview.vue'

const emit = defineEmits(['select'])
const toast = useToast()

const query = ref('')
const results = ref<any[]>([])
const searchLoading = ref(false)
const detailLoading = ref(false)
const entitiesLoading = ref(false)
const selecting = ref(false)
const showModal = ref(false)

const mangaDetail = ref<any | null>(null)
const mangaEntities = ref<any | null>(null)

const genreList = computed(() => (mangaDetail.value?.genres || []).map((g: any) => g.value).join(', '))

function notifyTenraiError(error: any, summary: string) {
    const data = error?.response?.data
    let detail: string
    if (data?.error === 'rate_limited') {
        const wait = data.retry_after ? ` Try again in ${data.retry_after}s.` : ' Try again in a few seconds.'
        detail = 'MyAnimeList is rate limiting requests.' + wait
    } else {
        detail = data?.message || data?.description || 'Could not reach MyAnimeList. Please try again.'
    }
    console.error(summary, data || error)
    toast.add({ severity: 'error', summary, detail, life: 4000 })
}

async function search() {
    if (query.value.trim().length < 3) return

    searchLoading.value = true
    results.value = []
    mangaDetail.value = null

    try {
        const res = await TenraiService.getMangaByQuery(query.value)
        results.value = res.data.items || []
        if (results.value.length) showModal.value = true
        else toast.add({ severity: 'info', summary: 'No matches', detail: `MyAnimeList has nothing for "${query.value.trim()}".`, life: 3000 })
    } catch (error) {
        results.value = []
        notifyTenraiError(error, 'Manga search failed')
    } finally {
        searchLoading.value = false
    }
}

async function fetchMangaDetail(mal_id: number) {
    detailLoading.value = true
    try {
        const res = await TenraiService.getMangaDetail(mal_id)
        mangaDetail.value = res.data
    } catch (error) {
        mangaDetail.value = null
        notifyTenraiError(error, 'Could not load manga details')
    } finally {
        detailLoading.value = false
    }
}

async function loadEntities(mal_id: number) {
    const res = await TenraiService.getMangaEntities(mal_id)
    return res.data
}

// "Load authors and characters" button: spins that button only.
async function fetchMangaEntities(mal_id: number) {
    entitiesLoading.value = true
    mangaEntities.value = null

    try {
        mangaEntities.value = await loadEntities(mal_id)
    } catch (error) {
        mangaEntities.value = null
        notifyTenraiError(error, 'Could not load characters and creators')
    } finally {
        entitiesLoading.value = false
    }
}

function clear() {
    query.value = ''
    results.value = []
    mangaDetail.value = null
    mangaEntities.value = null
    showModal.value = false
}

function closeModal() {
    showModal.value = false
    mangaDetail.value = null
    mangaEntities.value = null
}

async function selectManga() {
    if (!mangaDetail.value) return

    if (!mangaEntities.value) {
        selecting.value = true
        try {
            mangaEntities.value = await loadEntities(mangaDetail.value.mal_id)
        } catch (error) {
            mangaEntities.value = null
            notifyTenraiError(error, 'Could not load characters and creators')
        } finally {
            selecting.value = false
        }
    }

    emit('select', mangaDetail.value, mangaEntities.value)
    closeModal()
}
</script>

<style scoped>
.tile {
  display: block;
  width: 100%;
  padding: 8px;
  border-radius: 10px;
  border: 1px solid transparent;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.12s ease, background-color 0.12s ease;
}
.tile:hover { border-color: rgba(255, 255, 255, 0.12); background: rgba(255, 255, 255, 0.03); }
.tile:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
.meta dt { font-weight: 700; color: #64748b; }
.meta dd { color: #cbd5e1; }
</style>
