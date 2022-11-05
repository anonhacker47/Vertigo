<template>
  <div
    class="absolute top-0 right-0 bottom-0 left-0 min-h-screen bg-no-repeat bg-top bg-cover"
    :style="{ backgroundImage: 'url(' + image + ')' }"
  >
    <div
      class="flex flex-col min-h-screen min-w-screen"
      :style="`background: rgba(18,25,43,0.95);`"
    >
      <!-- <div class="min-h-screen" :style="`background-color: rgba${bg}`"> -->
      <HeaderItem />
      <div class="flex flex-row grow">
        <div class="flex flex-col z-50">
          <div class="flex flex-row z-50 basis-3/2">
            <img
              :src="image"
              alt=""
              class="md:h-[45vh] md:w-[15vw] rounded-lg mt-8 ml-16 border-4"
              :style="`border-color: rgb${bg}`"
            />
            <div class="flex flex-col mt-8 ml-8">
              <p
                class="text-5xl font-bold uppercase"
                :style="`color: rgb${bg}`"
              >
                {{ card.title }}
              </p>
              <p class="text-base text-white mt-4 font-normal">
                {{ card.summary }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-col z-50 basis-1/2"></div>
      </div>
    </div>
    <!-- <div class="text-4xl overflow-hidden text-black text-center font-bold bg-emerald-400 ">{{card.title}}</div> -->
    <!-- <div class="text-4xl overflow-hidden border-black border text-black text-center font-bold bg-red-600 ">{{card.series_format}}</div> -->
  </div>
</template>

<style scoped></style>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import HeaderItem from "../components/HeaderItem.vue";
import CardGetterService from "../services/CardGetterService";
import TokenService from "../services/TokenService";

const headers = TokenService.getTokenHeader("");
const route = useRoute("");
const card = ref("");
const bg = ref("");
const image = ref();

const props = defineProps({
  id: Number,
});

console.log("The id is: " + route.params.Id);

async function getCard() {
  try {
    const response = await CardGetterService.getcardbyid(route.params.Id, {
      headers,
    });
    card.value = response.data;
    bg.value =
      response.data.dominant_color.slice(0, -1) +
      response.data.dominant_color.slice(-1);
    // CardGetterService.getimagebyid(card.image).then()
    console.log(bg);
    image.value = await CardGetterService.getimagebyid(card.value.id);
    console.log(image.value);
  } catch (error) {
    // message.value = error;
    console.log(error);
  }
}

onMounted(() => {
  getCard();
});
</script>

<style scoped></style>
