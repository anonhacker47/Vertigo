<template>
    <div class="rounded-2xl border border-base-300 bg-base-100 p-4 shadow-sm">
        <div class="mb-2 flex items-center gap-2">
            <i class="pi pi-search text-lg"></i>
            <h3 class="text-sm font-semibold text-base-content">
                Search Manga (MyAnimeList)
            </h3>
        </div>

        <div class="flex gap-2">
            <InputText v-model="query" placeholder="Eg: Berserk" class="w-full" @keyup.enter="search" />
            <Button icon="pi pi-search" label="Search" iconPos="left" :loading="searchLoading" class="px-6"
                severity="primary" @click="search" />
            <Button icon="pi pi-times" label="Clear" class="px-4" outlined @click="clear" />
        </div>
    </div>

    <Dialog v-model:visible="showModal" modal header="Select Manga" class="w-[95vw] md:w-240">
        <div v-if="!mangaDetail && !detailLoading" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="item in results" :key="item.mal_id"
                class="cursor-pointer select-none rounded-xl border border-base-300 p-3 transition hover:border-primary"
                @click="fetchMangaDetail(item.mal_id)">
                <img :src="item.image_url" alt="Cover" class="w-full h-72 object-cover rounded-md mb-2" />
                <h4 class="font-semibold leading-tight">{{ item.name }}</h4>
                <p class="text-xs opacity-70">Year began: {{ item.year_began || '—' }}</p>
                <p class="mt-1 text-xs opacity-70">
                    {{ item.chapter_count || '?' }} chapters • {{ item.volume_count || '?' }} volumes
                </p>
            </div>
        </div>

        <div v-if="detailLoading" class="flex items-center justify-center py-24">
            <ProgressSpinner style="width:80px;height:80px" strokeWidth="4" animationDuration=".8s" />
        </div>

        <div v-if="mangaDetail" class="flex flex-col gap-4">
            <Button label="Back" icon="pi pi-arrow-left" class="w-fit" outlined
                @click="mangaDetail = null; mangaEntities = null" />

            <div class="flex flex-col gap-4 md:flex-row">
                <img :src="mangaDetail.image_url" alt="Cover" class="w-48 max-h-96 rounded-lg shadow md:w-64" />

                <div class="flex flex-col gap-2">
                    <h3 class="text-xl font-bold">{{ mangaDetail.name }}</h3>
                    <p class="text-sm opacity-70">
                        {{ mangaDetail.chapter_count || '?' }} chapters • {{ mangaDetail.volume_count || '?' }} volumes
                    </p>
                    <p class="text-sm opacity-70">Year: {{ mangaDetail.year_began }}</p>
                    <p class="text-sm opacity-70">Status: {{ mangaDetail.status }}</p>
                    <p class="text-sm opacity-70">
                        Genres: {{mangaDetail.genres.map(g => g.value).join(', ')}}
                    </p>
                    <p class="mt-2 text-sm">{{ mangaDetail.desc }}</p>

                    <div class="flex flex-row gap-4">
                        <Button as="a" :href="mangaDetail.mal_url" target="_blank" rel="noopener noreferrer"
                            label="View on MyAnimeList" icon="pi pi-external-link" severity="info" class="w-fit" />
                        <Button label="Load Authors & Characters" icon="pi pi-users" class="w-fit" severity="secondary"
                            :loading="entitiesLoading" @click="fetchMangaEntities(mangaDetail.mal_id)" />
                    </div>

                    <div v-if="entitiesLoading" class="flex justify-center py-8">
                        <ProgressSpinner style="width:60px;height:60px" strokeWidth="4" />
                    </div>

                    <div v-if="mangaEntities" class="mt-6 grid gap-6 md:grid-cols-2">
                        <div class="rounded-xl border border-base-300 p-4">
                            <h4 class="mb-2 text-sm font-semibold">
                                Authors ({{ mangaEntities.total_creators }})
                            </h4>
                            <ul class="space-y-1 text-sm">
                                <li v-for="creator in mangaEntities.creators" :key="creator.mal_id">
                                    • {{ creator.value }}
                                </li>
                            </ul>
                        </div>

                        <div class="rounded-xl border border-base-300 p-4">
                            <h4 class="mb-2 text-sm font-semibold">
                                Characters ({{ mangaEntities.total_characters }})
                            </h4>
                            <ul class="space-y-1 text-sm">
                                <li v-for="character in mangaEntities.characters" :key="character.mal_id">
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
            <Button v-if="mangaDetail" :label="`Select ${mangaDetail.name}`" severity="primary" @click="selectManga" />
        </template>
    </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import JikanService from '@/services/JikanService'

const emit = defineEmits(['select'])

const query = ref('')
const results = ref<any[]>([])
const searchLoading = ref(false)
const detailLoading = ref(false)
const entitiesLoading = ref(false)
const showModal = ref(false)

const mangaDetail = ref<any | null>(null)
const mangaEntities = ref<any | null>(null)

async function search() {
    if (query.value.trim().length < 3) return

    searchLoading.value = true
    results.value = []
    mangaDetail.value = null

    try {
        const res = await JikanService.getMangaByQuery(query.value)
        results.value = res.data.items || []
        if (results.value.length) showModal.value = true
    } catch {
        results.value = []
    } finally {
        searchLoading.value = false
    }
}

async function fetchMangaDetail(mal_id: number) {
    detailLoading.value = true
    try {
        const res = await JikanService.getMangaDetail(mal_id)
        mangaDetail.value = res.data
    } catch {
        mangaDetail.value = null
    } finally {
        detailLoading.value = false
    }
}

async function fetchMangaEntities(mal_id: number) {
    entitiesLoading.value = true
    mangaEntities.value = null

    try {
        const res = await JikanService.getMangaEntities(mal_id)
        mangaEntities.value = res.data
    } catch {
        mangaEntities.value = null
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
        try {
            entitiesLoading.value = true
            const res = await JikanService.getMangaEntities(mangaDetail.value.mal_id)
            mangaEntities.value = res.data
        } catch {
            mangaEntities.value = null
        } finally {
            entitiesLoading.value = false
        }
    }

    emit('select', mangaDetail.value, mangaEntities.value)
    closeModal()
}
</script>

<style scoped>
.p-button {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}
</style>
