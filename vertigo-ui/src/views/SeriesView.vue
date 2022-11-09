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
        <div class="flex flex-col z-50 basis-1/2">
          <div class="flex flex-row z-50">
            <img
              v-if="image != Image"
              :src="image"
              alt=""
              class="md:h-[45vh] md:w-[15vw] rounded-lg mt-8 ml-16 border-2"
              :style="`border-color: rgb${themecolor}`"
              @error="image = Image"
            />
            <div class="flex flex-col mt-8 ml-8">
              <p class="text-4xl font-bold" :style="`color: rgb${themecolor}`">
                {{ series.title }}
              </p>
              <p class="text-xl font-bold uppercase"
              :style="`color: rgb${themecolor}`">
                {{ series.publisher }}
              </p>
              <p class="text-base text-white mt-4 font-normal"
              :style="`color: rgb${themecolor}`">
                {{ series.summary }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-row justify-evenly z-50 pt-8 basis-1/2"></div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import HeaderItem from "../components/HeaderItem.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import TokenService from "../services/TokenService";

const headers = TokenService.getTokenHeader("");
const route = useRoute("");
const series = ref("");
const issue = ref("");
const themecolor = ref("");
const image = ref();
let Image = "noimage";

const props = defineProps({
  id: Number,
});

async function getSeries() {
  try {
    const response = await SeriesService.getSeriesbyId(route.params.Id, {
      headers,
    });
    series.value = response.data;
    themecolor.value =
      response.data.dominant_color.slice(0, -1) +
      response.data.dominant_color.slice(-1);
    image.value = SeriesService.getImagebyId(series.value.id);
  } catch (error) {
    // console.log(error);
  }
}

async function getIssues() {
  try {
    const response = await IssueService.getIssues(
      { headers },
      route.params.Id,
      "title",
      "asc"
    );
    issue.value = response.data;
    console.log(issue);
  } catch (error) {
    // message.value = error;
    console.log(error);
  }
}

onMounted(() => {
  getSeries(), getIssues();
});
</script>

<style scoped></style>
