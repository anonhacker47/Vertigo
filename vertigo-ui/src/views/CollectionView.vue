<template>
    <HeaderItem />
    <Transition enter-active-class="animate__animated animate__fadeIn"
      leave-active-class="animate__animated animate__fadeOut animate__faster">
      <div v-if="true" class="flex justify-around items-center py-2 border-b border-slate-700">
        <RouterLink :to="{ name: 'addnew' }" class="btn btn-primary justify-center">
          Add Series
        </RouterLink>
  
        <div class="dropdown">
          <button tabindex="0" class="btn m-1 focus:ring">
  <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" fill-rule="evenodd" class="focus:fill-black" clip-rule="evenodd">
    <path
      d="M12.01 20c-5.065 0-9.586-4.211-12.01-8.424 2.418-4.103 6.943-7.576 12.01-7.576 5.135 0 9.635 3.453 11.999 7.564-2.241 4.43-6.726 8.436-11.999 8.436zm-10.842-8.416c.843 1.331 5.018 7.416 10.842 7.416 6.305 0 10.112-6.103 10.851-7.405-.772-1.198-4.606-6.595-10.851-6.595-6.116 0-10.025 5.355-10.842 6.584zm10.832-4.584c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5zm0 1c2.208 0 4 1.792 4 4s-1.792 4-4 4-4-1.792-4-4 1.792-4 4-4z"
      fill="#a5f3fc" />
  </svg>
</button>
          <button tabindex="0"
            class="dropdown-content card p-2 ml-[-80px] md:ml-0 shadow bg-base-100 rounded-box w-64 md:w-80 z-20">
            <div class="label">
              <span class="font-bold text-lg text-sky-200 text-grey-500">Display Options</span>
            </div>
            <div class="label self-center pt-0">
              <span class="text-slate-200 text-sm">Items per line</span>
            </div>
            <div v-if="getScreenWidth() >= `500`" class="px-5">
              <input @change="changeGrid" type="range" min="2" max="10" :value="selectedGrid" class="range range-xs"
                step="1" />
            </div>
            <div v-if="getScreenWidth() >= `500`" class="w-full flex justify-between text-xs px-5">
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
              <span>6</span>
              <span>7</span>
              <span>8</span>
              <span>9</span>
              <span>10</span>
            </div>
            <div v-if="getScreenWidth() < `500`" class="px-5">
              <input @change="changeGrid" type="range" min="2" max="5" :value="selectedGrid" class="range range-xs"
                step="1" />
            </div>
            <div v-if="getScreenWidth() < `500`" class="w-full flex justify-between text-xs px-5">
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
            <div class="flex justify-between">
              <div class="label">
                <span class="font-bold text-lg text-sky-200">Sort By</span></div>
              <div class="flex">
                <input type="radio" id="asc" value="asc" name="asc" class="hidden" @click="sortByDirection" /><label
                  for="asc" class="label text-gray-400 label-text text-sm cursor-pointer">Asc</label>
                <input type="radio" id="desc" value="desc" name="asc" class="hidden cursor-pointer" @click="sortByDirection"
                  checked /><label for="desc" class="label text-gray-400 label-text text-sm">Desc</label>
              </div>
            </div>
            <div class="form-control px-3">
              <label class="label cursor-pointer">
                <span class="text-slate-200">Title</span>
                <input type="radio" name="sortby" class="radio checked:bg-red-500" @click="sortByProperties"
                  value="title" />
              </label>
            </div>
            <div class="form-control px-3">
              <label class="label cursor-pointer">
                <span class="text-slate-200">Date Added</span>
                <input type="radio" name="sortby" class="radio checked:bg-blue-500" @click="sortByProperties"
                  value="timestamp" checked />
              </label>
            </div>
          </button>
        </div>
  
        <button class="btn" :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }" @click="toggleDelete">
          Delete Mode
        </button>
      </div>
    </Transition>
    <div class="grid gap-3 md:pb-6 pt-2 pb-8 md:mx-5 mx-3 md:gap-5" :class="`grid-cols-${selectedGrid}`" id="carddiv">
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
              :textwidth="cardWidth" :have-fraction="calculatePercentage(card.owned_count, card.books_count)"
              :read-fraction="calculatePercentage(card.read_count, card.books_count)" />
          </RouterLink>
          <TransitionGroup enter-active-class="animate__animated animate__bounceIn"
            leave-active-class="animate__animated  animate__bounceOut">
            <div v-if="deleteMode" @click.prevent="deleteCard(card.id)"
              class=" absolute rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
              <img src="../assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
            </div>
          </TransitionGroup>
        </div>
      </TransitionGroup>
    </div>
  </template>
  
  <script setup>
  import HeaderItem from "../components/HeaderItem.vue";
  import CollectionCardItem from "../components/cards/CollectionCardItem.vue";
  import { onMounted, ref } from "vue";
  import SeriesService from "../services/SeriesService";
  import TokenService from "../services/TokenService";
  import PanelCardItem from "../components/cards/PanelCardItem.vue";
  import ActionButtonItem from "../components/buttons/ActionButtonItem.vue";
  import { id, order } from "@formkit/i18n";
  import { applyListeners } from "@formkit/observer";
  import { useUserStore } from "../store/user";
  import { useWindowSize } from 'vue-window-size';
  
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
  
  const calculatePercentage = (count, total) => {
    const percentage = `${(count / total) * 100}%`;
    console.log(`Calculated percentage: ${percentage}`);
    return percentage;
  }
  
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
  
  input:checked+label {
    border: 2px;
    color: #38bdf8;
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
  