<template>
  <Transition enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster">

    <div v-if="true"
      class="flex md:hidden flex-col md:flex-row justify-between items-center py-4 border-b bg-base-100 border-slate-700 px-4 md:px-12 gap-4">

      <div class="flex flex-col items-center text-center w-full md:w-auto">
        <h1 class="text-2xl md:text-3xl font-bold text-white">
          Series Collection
        </h1>
        <p class="text-sm text-slate-400 mt-1">
          Total series: {{ pagination.base_total }}
        </p>
      </div>

      <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid" :changeGrid="changeGrid"
        :orderDirection="orderDirection" :orderByProperties="orderByProperties" v-model:viewMode="viewMode"
        v-model:orderBy="orderBy" v-model:orderDir="orderDir" v-model:itemsPerPage="pagination.limit" />
      <div class="flex flex-row items-center justify-center w-full md:w-auto gap-4 md:gap-4">
        <RouterLink :to="{ name: 'AddSeries' }" class="btn btn-primary flex-1 md:flex-none">
          Add Series
        </RouterLink>
        <button class="btn flex-1 md:flex-none" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }"
          @click="toggleDelete">
          Delete Mode
        </button>
      </div>
    </div>
  </Transition>

  <Transition enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster">
    <div v-if="true"
      class="hidden md:flex flex-col md:flex-row justify-between items-center py-4 border-b bg-base-100 border-slate-700 gap-4">
      <div class="flex flex-col md:flex-row justify-between items-center container mx-auto">
        <RouterLink :to="{ name: 'AddSeries' }" class="btn btn-primary text-black!"> Add Series </RouterLink>
        <div class="md:ml-16 flex flex-col items-center text-center">
          <h1 class="text-3xl font-bold text-white"> Series Collection </h1>
          <p class="text-sm text-slate-400 mt-1"> Total series: {{ pagination.base_total }} </p>
        </div>
        <div class="flex flex-col md:flex-row items-center gap-2">
          <button class="btn" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }" @click="toggleDelete">
            Delete Mode </button>
        </div>
      </div>
    </div>
  </Transition>

  <div class="flex md:flex-row flex-col items-center justify-between py-4 w-full max-w-7xl mx-auto">
    <div class="hidden md:flex">
      <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid" :changeGrid="changeGrid"
        :orderDirection="orderDirection" :orderByProperties="orderByProperties" v-model:viewMode="viewMode"
        v-model:orderBy="orderBy" v-model:orderDir="orderDir" v-model:itemsPerPage="pagination.limit" />
    </div>
    <SearchSeriesForm @search="handleSearch" :initialFilters="currentFilter" />
  </div>

  <div v-if="loading" class="flex justify-center items-center py-60 col-span-full">
    <div class="flex justify-center items-center">
      <span class="loading-ring  text-success h-44 w-44 loading"></span>
    </div>
  </div>

  <!-- Card View -->
  <div v-else-if="viewMode == 'card'"
    :class="`grid gap-3 md:pb-6 md:gap-5 md:m-auto mx-2 max-w-screen-3xl grid-cols-${selectedGrid}`">
    <template v-if="seriesList.length > 0">
      <TransitionGroup :key="sortKey" enter-active-class="animate__animated animate__zoomInDown">
        <div class="flex flex-row relative justify-center items-start" v-for="series in seriesList" :key="series.id">
          <CollectionCard :series="series" :cardHeightMD="cardHeightMD"
            :cardWidthMD="cardWidthMD" :cardHeight="cardHeight" :cardWidth="cardWidth" :deleteMode="deleteMode"
            @confirmDelete="confirmDelete" />
        </div>
      </TransitionGroup>
    </template>
    <template v-else>
      <div class="text-center col-span-full py-10 text-slate-400">
        No series found. Start by adding a new one!
      </div>
    </template>
  </div>


  <Transition name="list" enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut">
    <div class="mx-5" v-if="viewMode === 'list'" key="listView">
      <CollectionTable v-if="seriesList && seriesList.length" :seriesList="seriesList" :deleteMode="deleteMode"
        :confirmDelete="confirmDelete" />
    </div>
  </Transition>

  <Paginator v-if="pagination.total" :rows="pagination.limit" :totalRecords="pagination.total"
    :first="pagination.offset" @page="onPageChange" class="mx-auto max-w-fit py-4" />

</template>

<script setup lang="ts">
import CollectionCard from "@/components/cards/CollectionCard.vue";
import CollectionTable from "../components/tables/CollectionTable.vue";
import { computed, onMounted, ref, watch } from "vue";
import SeriesService from "../services/SeriesService";
import { useUserStore } from "../store/user";
import { useUserPreferences } from "@/store/userPreferences";
import { useWindowSize } from "vue-window-size";
import CollectionDropDownMenu from "@/components/dropdowns/CollectionDropDownMenu.vue";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { Series } from "@/types/series.types";
import Paginator from "primevue/paginator";
import SearchSeriesForm from "@/components/forms/SearchSeriesForm.vue";
import { useConfirmAction } from "@/composables/useConfirmAction";
import { useRoute, useRouter } from "vue-router";

const onPageChange = (event: any) => {
  if (event.rows > 0) {
    getseriesList(currentFilter.value, event.first, event.rows);
  }
};

const toast = useToast();
const { confirmAction } = useConfirmAction();

const confirmDelete = (id: number, title: any) => {
  confirmAction({
    message: `Series ${title}`,
    header: "Confirm Deletion",
    acceptLabel: "Delete",
    severity: "danger",
    successMessage: `$Series ${title} deleted`,
    onAccept: () => {
      deleteSeries(id);
      toast.add({
        severity: "success",
        summary: "Confirmed",
        detail: `Series ${title} deleted`,
        life: 3000,
      });
    },
  });
};

const { width } = useWindowSize();
const seriesList = ref<Series[]>([]);
const userstore = useUserStore();
const userPreferences = useUserPreferences();
const message = ref();
const deleteMode = ref(false);
const selectedGrid = ref<number>(userPreferences.cardsPerLine);
const orderBy = ref(userPreferences.orderBy);
const orderDir = ref(userPreferences.orderDir);


const route = useRoute();
const router = useRouter();

const viewMode = computed({
  get: () => userPreferences.viewMode,
  set: (val) => userPreferences.setViewMode(val)
});

const sortKey = ref(true);
const loading = ref(false);

// Custom heights and width for each column vallues
// cardHeight for mobile devices
// cardHeightMD for larger devices

let cardHeightMultiplierMD = [34, 34, 30, 27, 21.5, 19, 16.3, 14, 13.5];
let cardWidthMultiplierMD = [22, 22, 20, 17.5, 14, 12, 10.5, 9.2, 8.2];
const cardHeightMD = ref(cardHeightMultiplierMD[selectedGrid.value - 2]);
const cardWidthMD = ref<number>(cardWidthMultiplierMD[selectedGrid.value - 2]);

let cardHeightMultiplier = [19, 14, 9, 7.5];
let cardWidthMultiplier = [12, 9.2, 6, 5];
const cardHeight = ref(cardHeightMultiplier[selectedGrid.value - 2]);
const cardWidth = ref(cardWidthMultiplier[selectedGrid.value - 2]);

const pagination = ref({
  total: 0,
  limit: 25,
  offset: 0,
  base_total:0
});

const currentFilter = ref({});

const handleSearch = (filters) => {
  currentFilter.value = filters;

  router.replace({
    query: {
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v)
      ),
      limit: pagination.value.limit.toString(),
    },
  });

  getseriesList(currentFilter.value, 0, pagination.value.limit);
};

watch(() => pagination.value.limit, (newLimit) => {
  router.replace({
    query: {
      ...route.query,
      limit: newLimit.toString(),
    },
  });
  getseriesList(currentFilter.value, 0, newLimit);
});

watch(selectedGrid, (newVal) => {
  cardHeightMD.value = cardHeightMultiplierMD[newVal - 2];
  cardWidthMD.value = cardWidthMultiplierMD[newVal - 2];
  cardHeight.value = cardHeightMultiplier[newVal - 2];
  cardWidth.value = cardWidthMultiplier[newVal - 2];

});

async function deleteSeries(id: number) {
  try {
    await SeriesService.removeSeries(id);
    getseriesList();
  } catch (error) {
    message.value = error;
  }

  console.log(message);
}

const toggleDelete = (): void => {
  deleteMode.value = !deleteMode.value;
};

const getseriesList = async (
  filter = currentFilter.value,
  offset = 0,
  limit = pagination.value.limit
) => {
  if (limit === 0) return;
  loading.value = true;
  try {
    const result: any = await SeriesService.fetchSeries(
      orderBy.value,
      orderDir.value,
      limit,
      offset,
      filter
    );
    seriesList.value = result.seriesList;
    pagination.value = result.pagination;
  } catch (error) {
    console.error("Error loading series:", error);
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to load series.",
      life: 3000,
    });
  } finally {
    loading.value = false; // stop loading
  }
};

function changeGrid(selected: any) {
  const newVal = parseInt(selected.target.value);
  userPreferences.setCardsPerLine(newVal);
  selectedGrid.value = newVal;
}

function orderDirection(values: any) {
  userPreferences.setorderDir(values.target.value);
  orderDir.value = values.target.value;
  seriesList.value = [];
  getseriesList();
}

function orderByProperties(values: any) {
  userPreferences.setorderBy(values.target.value);
  orderBy.value = values.target.value;
  seriesList.value = [];
  getseriesList();
}

function getScreenWidth() {
  const windowWidth = width.value;
  return windowWidth;
}

onMounted(() => {
  userPreferences.loadPreferences();

  const query = route.query;

  const filters = {
    query: query.query || "",
    genre: query.genre || "",
    creator: query.creator || "",
    character: query.character || "",
    publisher: query.publisher || "",
    series_format: query.series_format || "",
  };

  currentFilter.value = filters;

  getseriesList(
    filters,
    0,
    Number(query.limit) || pagination.value.limit
  );
});

watch(
  () => route.query,
  (newQuery) => {
    const filters = {
      query: newQuery.query || "",
      genre: newQuery.genre || "",
      creator: newQuery.creator || "",
      character: newQuery.character || "",
      publisher: newQuery.publisher || "",
      series_format: newQuery.series_format || "",
    };

    currentFilter.value = filters;
    getseriesList(filters, 0, pagination.value.limit);
  }
);



</script>

<style scoped>
.paneldiv {
  height: calc(100vh - 72px);
}

.background {
  background: var(--bg-gradient);
}

.drp {
  margin-left: -84px;
}

.range::-moz-range-thumb {
  color: #1fb2a6;
  box-shadow:
    0 0 0 3px #1fb2a6 inset,
    var(--focus-shadow, 0 0),
    calc(var(--filler-size) * -1 - var(--filler-offset)) 0 0 var(--filler-size);
}
</style>
