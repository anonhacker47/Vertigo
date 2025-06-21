<template>
  <Transition enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster">
    <div v-if="true" class="flex justify-around items-center py-2 border-b border-slate-700">
      <RouterLink :to="{ name: 'AddNewSeries' }" class="btn btn-primary justify-center">
        Add Series
      </RouterLink>

      <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid" :changeGrid="changeGrid"
        :orderDirection="orderDirection" :orderByProperties="orderByProperties" v-model:viewMode="viewMode"
        v-model:orderBy="orderBy" v-model:orderDir="orderDir" />
      <button class="btn" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }" @click="toggleDelete">
        Delete Mode
      </button>
    </div>
  </Transition>
  <div class="grid gap-3 md:pb-6 pt-2 md:gap-5 md:m-auto max-w-screen-3xl" v-if="viewMode == 'card'"
    :class="`grid-cols-${selectedGrid}`">
    <template v-if="seriesList.length > 0">
      <TransitionGroup :key="sortKey" enter-active-class="animate__animated animate__zoomInDown">
        <div class="flex flex-row relative justify-center items-start" v-for="series in seriesList" :key="series.id">

          <CollectionCardItem :class="{ 'animate-wiggle': deleteMode }" :series="series" :cardHeightMD="cardHeightMD"
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


  <ConfirmDialog>
    <template #message="slotProps">
      <p class="font-bold">
        Do you really want to delete the series
        <span class="text-red-500">{{ slotProps.message.message }}</span> ?
      </p>
    </template>
  </ConfirmDialog>

</template>

<script setup lang="ts">
import CollectionCardItem from "@/components/cards/CollectionCardItem.vue";
import CollectionTable from "../components/tables/CollectionTable.vue";
import { onMounted, ref } from "vue";
import SeriesService from "../services/SeriesService";
import { useUserStore } from "../store/user";
import { useUserPreferences } from "@/store/userPreferences";
import { useWindowSize } from 'vue-window-size';
import CollectionDropDownMenu from '@/components/dropdowns/CollectionDropDownMenu.vue';
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { Series } from '@/types/series.types';
import Paginator from 'primevue/paginator';

const onPageChange = (event: any) => {
  if (event.rows > 0) {
    getseriesList(event.first, event.rows);
  }
};

const confirm = useConfirm();
const toast = useToast();

const confirmDelete = (id: number, title: any) => {
  confirm.require({
    message: title,
    header: 'Confirm Deletion',
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger'
    },
    accept: () => {
      deleteSeries(id);
      toast.add({ severity: 'success', summary: 'Confirmed', detail: `${title} deleted`, life: 3000 });
    },
    reject: () => {
      // toast.add({ severity: 'error', summary: 'Rejected', detail: 'You have rejected', life: 3000 });
    }
  });
};

const { width } = useWindowSize();
const seriesList = ref<Series[]>([]);
const pagination = ref({
  total: 0,
  limit: 25,
  offset: 0
});
const userstore = useUserStore();
const userPreferences = useUserPreferences();
const { id: userId } = userstore.getUser();
const message = ref();
const deleteMode = ref(false);
const selectedGrid = ref<number>(userPreferences.cardsPerLine);
const orderBy = ref(userPreferences.orderBy);
const orderDir = ref(userPreferences.orderDir);

const viewMode = ref(userPreferences.viewMode); // Default to user preference

const sortKey = ref(true);

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


async function deleteSeries(id: number) {
  const idToRemove = id;
  seriesList.value.splice(
    seriesList.value.findIndex((a) => a.id === idToRemove),
    1
  );

  try {
    const response = await SeriesService.removeSeries(id);
    // setPrimaryKey();
    getseriesList();
  } catch (error) {
    message.value = error;
  }

  console.log(message);
}

const toggleDelete = (): void => {
  deleteMode.value = !deleteMode.value;
};

const getseriesList = async (offset = 0, limit = pagination.value?.limit || 25) => {
  if (limit === 0) return;

  try {
    const result: any = await SeriesService.fetchSeries(userId, orderBy.value, orderDir.value, limit, offset);
    seriesList.value = result.seriesList;
    pagination.value = result.pagination;
  } catch (error) {
    console.error('Error loading series:', error);
  }
};

function changeGrid(selected: any) {
  userPreferences.setCardsPerLine(selected.target.value);
  selectedGrid.value = parseInt(selected.target.value);
  cardHeightMD.value = cardHeightMultiplierMD[selectedGrid.value - 2];
  cardWidthMD.value = cardWidthMultiplierMD[selectedGrid.value - 2];
  cardHeight.value = cardHeightMultiplier[selectedGrid.value - 2];
  cardWidth.value = cardWidthMultiplier[selectedGrid.value - 2];
  console.log(selectedGrid.value);
}

function orderDirection(values: any) {
  userPreferences.setorderDir(values.target.value)
  orderDir.value = values.target.value;
  seriesList.value = []
  getseriesList();

}

function orderByProperties(values: any) {
  userPreferences.setorderBy(values.target.value);
  orderBy.value = values.target.value;
  seriesList.value = []
  getseriesList();
}

function getScreenWidth() {
  const windowWidth = width.value;
  return windowWidth;
}

onMounted(() => {
  userPreferences.loadPreferences();
  getseriesList(pagination.value.offset, 25);
});
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
  box-shadow: 0 0 0 3px #1fb2a6 inset, var(--focus-shadow, 0 0),
    calc(var(--filler-size) * -1 - var(--filler-offset)) 0 0 var(--filler-size);
}
</style>