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
      class="smallbutton text-black bg-[#7f76ee] hover:bg-[#5d55cc] hover:text-grey-100 rounded px-5 shadow-inner justify-center hover:shadow-lg inline-flex items-center "
      @click="toggleModal();cancelDelete()"
    >
      Add Series
    </button>
    <button
      class="bg-red-400 text-black hover:bg-red-500 rounded hover:bg-[bg-red-500] mx-3 px-5 py-2"
      :class="{'animate-wiggle': deleteMode,'bg-red-500': deleteMode}"
      @click="toggleDelete"
    >
      Delete Mode
    </button>
  </div>
  </Transition>
  <Transition
  enter-active-class="animate__animated animate__fadeIn"
      ><div
    v-if="modalOpen"
    class="z-50 h-full  fixed flex justify-center items-center pb-24 w-full background"
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
  </div></Transition>
  <div class="container flex-row flex-wrap justify-around flex px-5">
    <TransitionGroup
      enter-active-class="animate__animated animate__zoomInDown"
      leave-active-class="animate__animated animate__zoomOutDown"
    >
      <div
        class="flex flex-row items-start mr-5"
        v-for="card in cards"
        :key="card"
        id="carddiv"
      >
        <RouterLink
          class="shadow-2xl"
          :to="{ name: 'series', params: { Id: card.id+card.slug } }"
        >
          <SliderCardItem
            class="mt-10"
            :class="{'animate-wiggle': deleteMode}"
            :name="card.title"
            :src="card.thumbnail"
          /> </RouterLink
        ><TransitionGroup
          enter-active-class="animate__animated animate__bounceIn"
          leave-active-class="animate__animated animate__bounceOut"
          ><div
            v-if="deleteMode && !modalOpen"
            @click.prevent="deleteCard(card.id)"
            class="rounded hover:scale-105 mt-4  hover:rotate-180 z-[800] transition ease-in-out"
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

const cards = ref();
const message = ref();
const modalOpen = ref(false);
const deleteMode = ref(false);
const overflow = ref('auto');
const componentKey = ref();
const localid = ref();
const headers = TokenService.getToken();
const header = TokenService.getToken();

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
  window. scrollTo({top:0});
  overflow.value = (overflow.value=='auto' ? 'hidden' : 'auto');
  
  modalOpen.value = !modalOpen.value;
  document.body.style.overflow=`${overflow.value}`;
}

function toggleDelete() {
  deleteMode.value = !deleteMode.value;
}

function cancelDelete(){
  deleteMode.value = (deleteMode.value == true ? false :false);
}

// function show() {
//   console.log(cards);
// }

async function getCards() {
  try {
    const response = await CardGetterService.getcards({
      headers,
    });
    cards.value = response.data.data;
    console.log(cards);
  } catch (error) {
    message.value = error;
  }
  console.log(message);
}

function convertToSlug(Text) {
  return Text.toLowerCase()
             .replace(/ /g, '-')
             .replace(/[^\w-]+/g, '');
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
    console.log(localid.value);
    cards.value.unshift({
      id: local,
      slug:convertToSlug(title),
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
</style>
