<template>
  <div
    class="min-h-screen bg-no-repeat bg-top bg-cover  "
    :style="{ backgroundImage: 'url(' + image + ')' }"
  >
  <div class="min-h-screen" style="background-color: rgb(19, 25, 41,0.93)">
    <HeaderItem/>

    <!-- <div class="text-4xl overflow-hidden text-black text-center font-bold bg-emerald-400 ">{{card.title}}</div> -->
    <!-- <div class="text-4xl overflow-hidden border-black border text-black text-center font-bold bg-red-600 ">{{card.series_format}}</div> -->
</div>  </div>
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
    image.value = `http://localhost:5000/api/posts/images/${card.value.id}`;
    // console.log(card.value.title);
    console.log(image.value);
    // console.log(card);
    // console.log(response);
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
