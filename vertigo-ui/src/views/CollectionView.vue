<template>
  <div class="mx-auto w-full max-w-page px-4 pt-6 md:px-8">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Collection</h1>
        <p class="mt-1 text-sm font-semibold text-slate-400">{{ countLine }}</p>
      </div>
      <div class="flex items-center gap-2">
        <button type="button" class="iconbtn" :class="{ 'iconbtn--danger': deleteMode }" :aria-pressed="deleteMode"
          :title="deleteMode ? 'Leave delete mode' : 'Delete mode'" aria-label="Delete mode" @click="toggleDelete">
          <i class="pi pi-trash"></i>
        </button>
        <RouterLink :to="{ name: 'AddSeries' }" custom v-slot="{ navigate }">
          <Button label="Add series" icon="pi pi-plus" size="small" @click="navigate" />
        </RouterLink>
      </div>
    </div>

    <CollectionToolbar class="mt-5 border-b border-white/8 pb-4" :filters="currentFilter" :order-by="orderBy" :order-dir="orderDir"
      :view-mode="viewMode" :cards-per-line="selectedGrid" :items-per-page="pagination.limit"
      @update:filters="handleSearch" @update:sort="setSort" @update:view-mode="viewMode = $event"
      @update:cards-per-line="setCardsPerLine" @update:items-per-page="pagination.limit = $event" @clear="clearFilters" />
  </div>

  <div v-if="loading && !seriesList.length" class="mx-auto grid w-full max-w-page gap-3 px-4 pt-5 md:gap-5 md:px-8" :style="gridStyle" aria-hidden="true">
    <div v-for="n in skeletonCount" :key="n" class="aspect-2/3 animate-pulse rounded-md bg-white/6"></div>
  </div>

  <div v-else-if="!loading && !seriesList.length" class="mx-auto max-w-page px-4 py-20 text-center md:px-8">
    <p class="text-lg font-bold text-white">{{ hasFilters ? 'No series match these filters.' : 'No series yet.' }}</p>
    <p class="mt-2 text-sm font-semibold text-slate-400">{{ hasFilters ? 'Try fewer filters or a shorter search.' : 'Add a series and mark what you own.' }}</p>
    <div class="mt-5">
      <Button v-if="hasFilters" label="Clear filters" icon="pi pi-times" severity="secondary" size="small" @click="clearFilters" />
      <RouterLink v-else :to="{ name: 'AddSeries' }" custom v-slot="{ navigate }">
        <Button label="Add series" icon="pi pi-plus" size="small" @click="navigate" />
      </RouterLink>
    </div>
  </div>

  <div v-if="seriesList.length" class="pt-5" :class="{ 'pointer-events-none': loading }">
    <Transition name="view" mode="out-in">
      <div v-if="viewMode === 'card'" key="card" class="mx-auto grid w-full max-w-page gap-3 px-4 md:gap-5 md:px-8"
        :style="[gridStyle, { '--animate-duration': '0.4s' }]">
        <TransitionGroup :key="'results-' + resultsKey" :appear="animateResults" enter-active-class="animate__animated animate__zoomInDown">
          <div v-for="series in seriesList" :key="series.id" class="relative min-w-0">
            <CollectionCard :series="series" :image-url="series.thumbnail" :deleteMode="deleteMode" @confirmDelete="confirmDelete" />
          </div>
        </TransitionGroup>
      </div>

      <div v-else key="list" class="mx-auto w-full max-w-page px-4 md:px-8">
        <CollectionTable :seriesList="seriesList" :deleteMode="deleteMode" :confirmDelete="confirmDelete" />
      </div>
    </Transition>
  </div>

  <CollectionPager :total="pagination.total" :limit="pagination.limit" :offset="pagination.offset" @page="onPageChange" />
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useConfirmAction } from "@/composables/useConfirmAction";
import { useUserPreferences } from "@/store/userPreferences";
import SeriesService from "@/services/SeriesService";
import type { Series } from "@/types/series.types";
import CollectionCard from "@/components/cards/CollectionCard.vue";
import CollectionTable from "@/components/tables/CollectionTable.vue";
import CollectionToolbar, { type SeriesFilters } from "@/components/collection/CollectionToolbar.vue";
import CollectionPager from "@/components/collection/CollectionPager.vue";

const EMPTY_FILTERS: SeriesFilters = { query: "", genre: "", creator: "", character: "", publisher: "", series_format: "" };

const toast = useToast();
const { confirmAction } = useConfirmAction();
const route = useRoute();
const router = useRouter();
const userPreferences = useUserPreferences();

const seriesList = ref<Series[]>([]);
const deleteMode = ref(false);
const selectedGrid = ref<number>(userPreferences.cardsPerLine);
const orderBy = ref(userPreferences.orderBy);
const orderDir = ref(userPreferences.orderDir);
const resultsKey = ref(0);       // bumped after every fetch so the card group remounts with the new rows
const animateResults = ref(false); // true only for the render right after a fetch, so a view switch stays quiet
const loading = ref(false);
const pagination = ref({ total: 0, limit: 25, offset: 0, base_total: 0 });
const currentFilter = ref<SeriesFilters>({ ...EMPTY_FILTERS });

const viewMode = computed({
  get: () => userPreferences.viewMode,
  set: (val) => userPreferences.setViewMode(val),
});

const hasFilters = computed(() => Object.values(currentFilter.value).some((v) => v));
const gridStyle = computed(() => ({ gridTemplateColumns: `repeat(${selectedGrid.value}, minmax(0, 1fr))` }));
const skeletonCount = computed(() => Math.min(pagination.value.limit || 10, 15));
const countLine = computed(() => {
  const total = pagination.value.base_total ?? 0;
  if (hasFilters.value) return `${pagination.value.total} of ${total} series`;
  return `${total} ${total === 1 ? "series" : "series"}`;
});

function filtersFromQuery(query: Record<string, any>): SeriesFilters {
  return {
    query: query.query || "",
    genre: query.genre || "",
    creator: query.creator || "",
    character: query.character || "",
    publisher: query.publisher || "",
    series_format: query.series_format || "",
  };
}

const getseriesList = async (filter = currentFilter.value, offset = 0, limit = pagination.value.limit) => {
  if (limit === 0) return;
  loading.value = true;
  try {
    const result: any = await SeriesService.fetchSeries(orderBy.value, orderDir.value, limit, offset, filter);
    seriesList.value = result.seriesList.map((series: Series) => ({
      ...series,
      thumbnail: SeriesService.getSeriesImageById(series.id, series.last_updated),
    }));
    pagination.value = result.pagination;
    resultsKey.value++;
    animateResults.value = true;
    await nextTick();
    animateResults.value = false;
  } catch (error) {
    console.error("Error loading series:", error);
    toast.add({ severity: "error", summary: "Error", detail: "Failed to load series.", life: 3000 });
  } finally {
    loading.value = false;
  }
};

// filters mirror into the URL, and the URL watcher refetches, so a link is a saved search
const handleSearch = (filters: SeriesFilters) => {
  currentFilter.value = filters;
  router.replace({
    query: {
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
      limit: pagination.value.limit.toString(),
    },
  });
};

function clearFilters() {
  handleSearch({ ...EMPTY_FILTERS });
}

function setSort({ orderBy: by, orderDir: dir }: { orderBy: string; orderDir: string }) {
  userPreferences.setorderBy(by);
  userPreferences.setorderDir(dir as "asc" | "desc");
  orderBy.value = by;
  orderDir.value = dir;
  getseriesList(currentFilter.value, 0, pagination.value.limit);
}

function setCardsPerLine(n: number) {
  userPreferences.setCardsPerLine(n);
  selectedGrid.value = n;
}

function onPageChange(event: { first: number; rows: number }) {
  getseriesList(currentFilter.value, event.first, event.rows);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

watch(() => pagination.value.limit, (newLimit) => {
  router.replace({ query: { ...route.query, limit: newLimit.toString() } });
  getseriesList(currentFilter.value, 0, newLimit);
});

watch(() => route.query, (newQuery) => {
  currentFilter.value = filtersFromQuery(newQuery);
  getseriesList(currentFilter.value, 0, pagination.value.limit);
});

const toggleDelete = () => {
  deleteMode.value = !deleteMode.value;
};

async function deleteSeries(id: number) {
  try {
    await SeriesService.removeSeries(id);
    getseriesList();
  } catch (error) {
    console.error(error);
  }
}

const confirmDelete = (id: number, title: string) => {
  confirmAction({
    message: `Series ${title}`,
    header: "Confirm Deletion",
    acceptLabel: "Delete",
    severity: "danger",
    successMessage: `Series ${title} deleted`,
    onAccept: () => {
      deleteSeries(id);
      toast.add({ severity: "success", summary: "Confirmed", detail: `Series ${title} deleted`, life: 3000 });
    },
  });
};

onMounted(() => {
  userPreferences.loadPreferences();
  currentFilter.value = filtersFromQuery(route.query);
  getseriesList(currentFilter.value, 0, Number(route.query.limit) || pagination.value.limit);
});
</script>

<style scoped>
/* Card/list crossfade: quick out, slightly slower in, so the new view settles rather than pops. */
.view-enter-active { transition: opacity 0.18s ease-out; }
.view-leave-active { transition: opacity 0.12s ease-in; }
.view-enter-from,
.view-leave-to { opacity: 0; }
@media (prefers-reduced-motion: reduce) {
  .view-enter-active,
  .view-leave-active { transition: none; }
}

.iconbtn {
  display: inline-flex;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  transition: color 0.12s ease, border-color 0.12s ease, background-color 0.12s ease;
}
.iconbtn:hover { color: #fff; border-color: rgba(255, 255, 255, 0.22); }
.iconbtn--danger { color: #fff; background: #dc2626; border-color: #dc2626; }
.iconbtn:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
</style>
