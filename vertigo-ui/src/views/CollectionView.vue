<template>
  <Transition enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster">
    <div v-if="true" class="flex justify-around items-center py-2 border-b border-slate-700">
      <RouterLink :to="{ name: 'addnew' }" class="btn btn-primary justify-center">
        Add Series
      </RouterLink>

      <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid" :changeGrid="changeGrid"
        :orderbyDirection="orderbyDirection" :orderbyProperties="orderbyProperties" v-model:viewMode="viewMode" />

      <button class="btn" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }" @click="toggleDelete">
        Delete Mode
      </button>
    </div>
  </Transition>
  <div class="grid gap-3 md:pb-6 pt-2 pb-8 md:mx-5 mx-3 md:gap-5" v-if="viewMode == 'card'"
    :class="`grid-cols-${selectedGrid}`" id="carddiv">
    <TransitionGroup :key="sortKey" enter-active-class="animate__animated animate__zoomInDown">
      <div class="flex flex-row relative justify-center items-start" v-for="series in seriesList" :key="series.id">

        <CollectionCardItem :class="{ 'animate-wiggle': deleteMode }" :series="series" :cardHeightMD="cardHeightMD"
          :cardWidthMD="cardWidthMD" :cardHeight="cardHeight" :cardWidth="cardWidth" :deleteMode="deleteMode"
          @confirmDelete="confirmDelete" />

      </div>
    </TransitionGroup>
  </div>
  <Transition name="list" enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut">
    <div class="mx-5 pb-10" v-if="viewMode === 'list'" key="listView">
      <CollectionTable v-if="seriesList && seriesList.length" :seriesList="seriesList" :deleteMode="deleteMode"
        :confirmDelete="confirmDelete" />
    </div>
  </Transition>
  <NotificationToast position="bottom-center" />
  <ConfirmDialog>
    <template #message="slotProps">
      <p class="font-bold">
        Do you really want to delete the series
        <span class="text-red-500">{{ slotProps.message.message }}</span>?
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
      deleteCard(id);
      toast.add({ severity: 'error', summary: 'Confirmed', detail: `${title} deleted`, life: 3000 });
    },
    reject: () => {
      // toast.add({ severity: 'error', summary: 'Rejected', detail: 'You have rejected', life: 3000 });
    }
  });
};

const { width } = useWindowSize();
const seriesList = ref<Series[]>([]);
const pagination = ref({});
const userstore = useUserStore();
const userId = userstore.getUser();
const message = ref();
const deleteMode = ref(false);
const headers = userstore.getTokenHeader();
const selectedGrid = ref<number>(4);
const orderby = ref("timestamp");
const orderdir = ref("desc");

const viewMode = ref("card"); // Default to card mode

const sortKey = ref(true);
// Custom heights and width for each column vallues
// cardHeight for mobile devices
// cardHeightMD for larger devices

let cardHeightMultiplierMD = [34, 34, 32, 27, 21.5, 19, 16.3, 14, 13.5];
let cardWidthMultiplierMD = [22, 22, 21, 17.5, 14, 12, 10.5, 9.2, 8.2];
const cardHeightMD = ref(cardHeightMultiplierMD[selectedGrid.value - 2]);
const cardWidthMD = ref<number>(cardWidthMultiplierMD[selectedGrid.value - 2]);

let cardHeightMultiplier = [19, 14, 9, 7.5];
let cardWidthMultiplier = [12, 9.2, 6, 5];
const cardHeight = ref(cardHeightMultiplier[selectedGrid.value - 2]);
const cardWidth = ref(cardWidthMultiplier[selectedGrid.value - 2]);


async function deleteCard(id:number) {
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

// async function setPrimaryKey() {
//   try {
//     const response = await SeriesService.getSeriesKey(
//     );
//     localStorage.setItem("key", response.data)
//   } catch (error) {
//     console.log(error);
//   }
// }

// async function getPostImages(id){
//   console.log(id);
//   try {
//   const response = await SeriesService.getimagebyid(
//     id,{headers}
//   )
//   .then(function (response) {
//     var imgUrl = 'data:image/jpeg;base64,' + btoa(new Uint8Array(response.data).reduce((data, byte) => data + String.fromCharCode(byte), '')
//     console.log(imgUrl);
//   })
//   } catch (error) {
//     message.value = error;
//     console.log(message);
//   }
// }


const getseriesList = async () => {
  try {
    const result: any = await SeriesService.fetchSeries(userId, orderby.value, orderdir.value);
    seriesList.value = result.seriesList;
    pagination.value = result.pagination;
  } catch (error) {
    console.error('Error loading series:', error);
  }
};


function changeGrid(selected: any) {
  selectedGrid.value = parseInt(selected.target.value);
  cardHeightMD.value = cardHeightMultiplierMD[selectedGrid.value - 2];
  cardWidthMD.value = cardWidthMultiplierMD[selectedGrid.value - 2];
  cardHeight.value = cardHeightMultiplier[selectedGrid.value - 2];
  cardWidth.value = cardWidthMultiplier[selectedGrid.value - 2];
  console.log(selectedGrid.value);
}

function orderbyDirection(values: any) {
  orderdir.value = values.target.value;
  seriesList.value = []
  getseriesList();

}

function orderbyProperties(values: any) {
  orderby.value = values.target.value;
  seriesList.value = []
  getseriesList();
}

function getScreenWidth() {
  const windowWidth = width.value;
  return windowWidth;
}

onMounted(() => {
  getseriesList();
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
  