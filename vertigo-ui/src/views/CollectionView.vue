<template>
  <Transition enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster">
    <div v-if="true" class="flex justify-around items-center py-2 border-b border-slate-700">
      <RouterLink :to="{ name: 'addnew' }" class="btn btn-primary justify-center">
        Add Series
      </RouterLink>

      <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid" :changeGrid="changeGrid" :sortByDirection="sortByDirection" :sortByProperties="sortByProperties" v-model:viewMode="viewMode" />

      <button class="btn" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }" @click="toggleDelete">
        Delete Mode
      </button>
    </div>
  </Transition>
   <div class="grid gap-3 md:pb-6 pt-2 pb-8 md:mx-5 mx-3 md:gap-5" v-if="viewMode == 'card'" :class="`grid-cols-${selectedGrid}`" id="carddiv">
      <TransitionGroup enter-active-class="animate__animated animate__zoomInDown">
        <div class="flex flex-row  relative justify-center items-start" v-for="card in cards" :key="card">
          <RouterLink class="shadow-2xl pt-4"
            :class="[`md:h-[${cardHeightMD}rem]`, `md:w-[${cardWidthMD}rem]`, `h-[${cardHeight}rem]`, `w-[${cardWidth}rem]`]"
            :to="{
              name: 'series',
              params: { Link: card.slug, Id: card.id },
              id: card.id,
            }">
            <CollectionCardItem :class="{ 'animate-wiggle': deleteMode }" :name="card.title" class="h-full w-full"
              :src="SeriesService.getImagebyId(card.id)" :format="card.series_format" :textwidth-m-d="cardWidthMD"
              :textwidth="cardWidth" :ownedCount="card.owned_count" :readCount="card.read_count" :issueCount="card.issue_count" /> 

          </RouterLink>
          <TransitionGroup enter-active-class="animate__animated animate__bounceIn"
            leave-active-class="animate__animated  animate__bounceOut">
            <div v-if="deleteMode" @click.prevent="confirmDelete(card.id,card.title)"
              class=" absolute rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
              <img src="../assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
            </div>
          </TransitionGroup>
        </div>
      </TransitionGroup>
    </div> 
  <div class="mx-5 pb-10" v-if="viewMode == 'list'">
    <CollectionTable :cards="cards" v-if="cards && cards.length" :deleteMode="deleteMode" :confirmDelete="confirmDelete" />
  </div>
    <NotificationToast position="bottom-center" />
  <ConfirmDialog>
    <template #message="slotProps">
      <p class="font-bold">
      Do you really want to delete the series 
      <span class="text-red-500">{{ slotProps.message.message  }}</span>?
    </p>
      </template>
  </ConfirmDialog>
</template>
  
<script setup>
import HeaderItem from "../components/HeaderItem.vue";
import CollectionCardItem from "../components/cards/CollectionCardItem.vue";
import CollectionTable from "../components/tables/CollectionTable.vue";
import { onMounted, ref } from "vue";
import SeriesService from "../services/SeriesService";
import TokenService from "../services/TokenService";
import PanelCardItem from "../components/cards/PanelCardItem.vue";
import ActionButtonItem from "../components/buttons/ActionButtonItem.vue";
import { id, order } from "@formkit/i18n";
import { applyListeners } from "@formkit/observer";
import { useUserStore } from "../store/user";
import { useWindowSize } from 'vue-window-size';
import CollectionDropDownMenu from '@/components/dropdowns/CollectionDropDownMenu.vue';
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

const confirm = useConfirm();
const toast = useToast();

const confirmDelete = (id,title) => {
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
const cards = ref();
const userstore = useUserStore();
const userId = TokenService.getUser();
const message = ref();
const deleteMode = ref(false);
const headers = TokenService.getTokenHeader();
const selectedGrid = ref(
  localStorage.getItem("gridCol") ? localStorage.getItem("gridCol") : 4
);
const orderby = ref("timestamp");
const orderdir = ref("desc");

const viewMode = ref("card"); // Default to card mode

// Custom heights and width for each column vallues
// cardHeight for mobile devices
// cardHeightMD for larger devices

let cardHeightMultiplierMD = [34, 34, 32, 27, 21.5, 19, 16.3, 14, 13.5];
let cardWidthMultiplierMD = [22, 22, 21, 17.5, 14, 12, 10.5, 9.2, 8.2];
const cardHeightMD = ref(cardHeightMultiplierMD[selectedGrid.value - 2]);
const cardWidthMD = ref(cardWidthMultiplierMD[selectedGrid.value - 2]);

let cardHeightMultiplier = [19, 14, 9, 7.5];
let cardWidthMultiplier = [12, 9.2, 6, 5];
const cardHeight = ref(cardHeightMultiplier[selectedGrid.value - 2]);
const cardWidth = ref(cardWidthMultiplier[selectedGrid.value - 2]);


async function deleteCard(id) {
  const idToRemove = id;
  cards.value.splice(
    cards.value.findIndex((a) => a.id === idToRemove),
    1
  );

  try {
    const response = await SeriesService.removeSeries(id, { headers });
    setPrimaryKey();
  } catch (error) {
    message.value = error;
  }

  console.log(message);
}

function toggleDelete() {
  deleteMode.value = !deleteMode.value;
}

async function setPrimaryKey() {
  try {
    const response = await SeriesService.getSeriesKey(
      { headers }
    );
    localStorage.setItem("key", response.data)
  } catch (error) {
    console.log(error);
  } 
}

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


async function getCards() {
  try {
    const response = await SeriesService.getSeries(
      { headers },
      userId,
      orderby.value,
      orderdir.value
    );
    cards.value = response.data.data;
    console.log(cards.value);
    // console.log(response);
  } catch (error) {
    message.value = error;
    console.log(error);
  }
}

function changeGrid(selected) {
  selectedGrid.value = parseInt(selected.target.value);
  localStorage.setItem("gridCol", selected.target.value);
  cardHeightMD.value = cardHeightMultiplierMD[selectedGrid.value - 2];
  cardWidthMD.value = cardWidthMultiplierMD[selectedGrid.value - 2];
  cardHeight.value = cardHeightMultiplier[selectedGrid.value - 2];
  cardWidth.value = cardWidthMultiplier[selectedGrid.value - 2];
  console.log(selectedGrid.value);
}

function sortByDirection(values) {
  orderdir.value = values.target.value;
  getCards();
}

function sortByProperties(values) {
  orderby.value = values.target.value;
  console.log(orderby);
  getCards();
}

function getScreenWidth() {
  const windowWidth = width.value;
  return windowWidth;
}

onMounted(() => {
  getCards();
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
  