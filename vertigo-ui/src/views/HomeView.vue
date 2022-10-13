<template>
  <HeaderItem />
  <Transition
    enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut animate__faster"
  >
    <div
      v-if="!modalOpen"
      class="flex justify-around py-5 border-b border-slate-700"
    >
      <button
        class="smallbutton text-black bg-[#7f76ee] hover:bg-[#5d55cc] hover:text-grey-100 rounded px-5 shadow-inner justify-center hover:shadow-lg inline-flex items-center"
        @click="
          toggleModal();
          cancelDelete();
        "
      >
        Add Series
      </button>

      <div class="dropdown">
        <label tabindex="0" class="btn m-1 focus:ring"
          ><svg
            width="24"
            height="24"
            xmlns="http://www.w3.org/2000/svg"
            fill-rule="evenodd"
            class="focus:fill-black"
            clip-rule="evenodd"
          >
            <path
              d="M12.01 20c-5.065 0-9.586-4.211-12.01-8.424 2.418-4.103 6.943-7.576 12.01-7.576 5.135 0 9.635 3.453 11.999 7.564-2.241 4.43-6.726 8.436-11.999 8.436zm-10.842-8.416c.843 1.331 5.018 7.416 10.842 7.416 6.305 0 10.112-6.103 10.851-7.405-.772-1.198-4.606-6.595-10.851-6.595-6.116 0-10.025 5.355-10.842 6.584zm10.832-4.584c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5zm0 1c2.208 0 4 1.792 4 4s-1.792 4-4 4-4-1.792-4-4 1.792-4 4-4z"
              fill="#a5f3fc"
            />
            </svg></label>
        <div
          tabindex="0"
          class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-80"
        >
          <label class="label">
            <span class="font-bold text-lg text-sky-200 text-grey-500"
              >Display Options</span
            >
          </label>
          <label class="label self-center pt-0">
            <span class="text-slate-200 text-sm">Items per line</span>
          </label>
          <div class="px-5">
            <input
              @change="changeGrid"
              type="range"
              min="3"
              max="7"
              value="4"
              class="range range-xs"
              step="1"
            />
          </div>
          <div class="w-full flex justify-between text-xs px-5">
            <span>3</span>
            <span>4</span>
            <span>5</span>
            <span>6</span>
            <span>7</span>
          </div>
          <div class="flex justify-between">
            <label class="label">
              <span class="font-bold text-lg text-sky-200">Sort By</span></label
            >
            <div class="flex">
              <input
                type="radio"
                id="asc"
                value="asc"
                name="asc"
                class="hidden"
                @click="sortByDirection"
              /><label
                for="asc"
                class="label text-gray-400 label-text text-sm cursor-pointer"
                >Asc</label
              >
              <input
                type="radio"
                id="desc"
                value="desc"
                name="asc"
                class="hidden cursor-pointer"
                @click="sortByDirection"
                checked
              /><label for="desc" class="label text-gray-400 label-text text-sm"
                >Desc</label
              >
            </div>
          </div>
          <div class="form-control px-3">
            <label class="label cursor-pointer">
              <span class="text-slate-200">Title</span>
              <input
                type="radio"
                name="sortby"
                class="radio checked:bg-red-500"
                @click="sortByProperties"
                value="title"
              />
            </label>
          </div>
          <div class="form-control px-3">
            <label class="label cursor-pointer">
              <span class="text-slate-200">Date Added</span>
              <input
                type="radio"
                name="sortby"
                class="radio checked:bg-blue-500"
                @click="sortByProperties"         
                value="timestamp"       
                checked
              />
            </label>
          </div>
        </div>
      </div>

      <button
        class="bg-red-400 text-black hover:bg-red-500 rounded hover:bg-[bg-red-500] mx-3 px-5 py-2"
        :class="{ 'animate-wiggle': deleteMode, 'bg-red-500': deleteMode }"
        @click="toggleDelete"
      >
        Delete Mode
      </button>
    </div>
  </Transition>
  <Transition enter-active-class="animate__animated animate__fadeIn"
    ><div
      v-if="modalOpen"
      class="z-50 h-full fixed flex justify-center items-center pb-24 w-full background"
    >
      <PanelCardItem
        ><div>
          <FormKit type="form" submit-label="Create" @submit="addCard">
            <FormKit
              type="text"
              name="title"
              label="Series Name"
              validation="required"
              label-class="mx-5"
            />
            <FormKit
              type="text"
              name="thumbnail"
              label="Image Link"
              default="meh"
            />
          </FormKit>
          <button
            class="bg-red-400 w-full text-black rounded px-6 py-2"
            @click="toggleModal"
          >
            Cancel
          </button>
        </div>
      </PanelCardItem>
    </div></Transition
  >
  <div class="container grid px-8 pb-8" :class="`grid-cols-${selectedGrid}`" id="carddiv">
    <TransitionGroup
      enter-active-class="animate__animated animate__zoomInDown"
    >
      <div
        class="flex flex-row justify-center items-start"
        v-for="card in cards"
        :key="card"
      >
        <RouterLink
          class="shadow-2xl"
          :to="{ name: 'series', params: { Id: card.id + card.slug } }"
        >
          <SliderCardItem
            class="mt-8"
            :class="{ 'animate-wiggle': deleteMode }"
            :name="card.title"
            :src="card.thumbnail"
            :grid="selectedGrid"
            :key="selectedGrid"
          /> </RouterLink
        ><TransitionGroup
          enter-active-class="animate__animated animate__bounceIn"
          leave-active-class="animate__animated animate__bounceOut"
          ><div
            v-if="deleteMode && !modalOpen"
            @click.prevent="deleteCard(card.id)"
            class="rounded hover:scale-105 mt-4 hover:rotate-180 z-[800] transition ease-in-out"
          >
            <img
              src="../assets/remove.svg"
              alt=""
              height="30"
              width="30"
            /></div
        ></TransitionGroup></div
    ></TransitionGroup>
  </div>
</template>

<script setup>
import HeaderItem from "../components/HeaderItem.vue";
import SliderCardItem from "../components/cards/SliderCardItem.vue";
import { onMounted, ref } from "vue";
import CardGetterService from "../services/CardGetterService";
import TokenService from "../services/TokenService";
import PanelCardItem from "../components/cards/PanelCardItem.vue";
import ActionButtonItem from "../components/buttons/ActionButtonItem.vue";
import { order } from "@formkit/i18n";

const cards = ref();
const message = ref();
const modalOpen = ref(false);
const deleteMode = ref(false);
const overflow = ref("auto");
const localid = ref();
const headers = TokenService.getTokenHeader();
const selectedGrid = ref(4);
const orderby = ref("timestamp");
const orderdir = ref("desc");

async function deleteCard(id) {
  const idToRemove = id;
  cards.value.splice(
    cards.value.findIndex((a) => a.id === idToRemove),
    1
  );

  try {
    const response = await CardGetterService.removepost(id, { headers });
    console.log("removed");
  } catch (error) {
    message.value = error;
  }

  console.log(message);
}

function toggleModal() {
  window.scrollTo({ top: 0 });
  overflow.value = overflow.value == "auto" ? "hidden" : "auto";

  modalOpen.value = !modalOpen.value;
  document.body.style.overflow = `${overflow.value}`;
}

function toggleDelete() {
  deleteMode.value = !deleteMode.value;
}

function cancelDelete() {
  deleteMode.value = deleteMode.value == true ? false : false;
}

async function getCards() {
  try {
    const response = await CardGetterService.getcards(
      { headers },
      orderby.value,
      orderdir.value
    );
    cards.value = response.data.data;
    console.log(cards);
    // console.log(response);
  } catch (error) {
    message.value = error;
  }
}

function convertToSlug(Text) {
  return Text.toLowerCase()
    .replace(/ /g, "-")
    .replace(/[^\w-]+/g, "");
}

async function addCard(values) {
  const title = values.title;
  var thumbnail = values.thumbnail;
  thumbnail ??= "string";

  var local = cards.value[0] == undefined ? 1 : cards.value[0]["id"] + 1;

  try {
    const response = await CardGetterService.addpost(
      { title, thumbnail },
      { headers }
    );
    localid.value = local;
    // console.log(localid.value);
    cards.value.unshift({
      id: local,
      slug: convertToSlug(title),
      title: title,
      thumbnail: thumbnail,
    });
    // getCards();
    toggleModal();
  } catch (error) {
    message.value = error;
  }

  console.log(message);
}

function changeGrid(selected) {
  selectedGrid.value = parseInt(selected.target.value);
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

input:checked + label {
  border: 2px;
  color: #38bdf8;
}
.range::-moz-range-thumb{
  color: #1FB2A6;
  box-shadow: 0 0 0 3px #1FB2A6 inset, var(--focus-shadow, 0 0), calc(var(--filler-size) * -1 - var(--filler-offset)) 0 0 var(--filler-size);
}
</style>
