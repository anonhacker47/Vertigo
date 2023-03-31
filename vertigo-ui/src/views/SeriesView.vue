<template>
  <div
    class="top-0 right-0 bottom-0 left-0 bg-no-repeat bg-center bg-cover"
    :style="{ backgroundImage: 'url(' + image + ')' }"
  >
    <div
      class="flex flex-col min-h-screen min-w-screen"
      :style="`background: rgba(18,25,43,0.95);`"
    >
      <!-- <div class="min-h-screen" :style="`background-color: rgba${bg}`"> -->
      <HeaderItem />
      <div class="flex flex-col grow">
        <div class="flex flex-row basis-1/2">
          <div class="flex flex-row pb-6 basis-1/2 z-50">
            <img
              v-if="image != Image"
              :src="image"
              alt=""
              class="md:h-[45vh] md:w-[15vw] rounded-lg mt-8 ml-16 border-2"
              :style="`border-color: rgb${themecolor}`"
              @error="image = Image"
            />
            <div class="flex flex-col mt-8 ml-8">
              <p class="text-5xl font-bold" :style="`color: rgb${themecolor}`">
                {{ series.title }}
              </p>
              <p
                class="text-xl font-bold uppercase"
                :style="`color: rgb${themecolor}`"
              >
                {{ series.publisher }}
              </p>
              <p
                class="text-base text-white mt-4 font-normal"
                :style="`color: rgb${themecolor}`"
              >
                {{ series.summary }}
              </p>
            </div>
          </div>
          <div class="basis-1/2"></div>
        </div>
        <div class="flex flex-col basis-1/2">
          <div
            class="flex flex-col overflow-x-scroll flex-grow w-full m-auto p-auto"
          >
            <h1
              class="flex pb-5 lg:px-20 md:px-10 px-5 lg:mx-40 md:mx-20 mx-5 font-bold text-4xl"
              :style="`color: rgb${themecolor}`"            
              >
              Issues
            </h1>
            <div class="flex overflow-x-scroll pb-10 hide-scroll-bar">
              <div class="flex flex-nowrap lg:ml-60 md:ml-20 ml-10">
                <div
                  class="flex flex-row justify-center items-start"
                  v-for="issue in issues"
                  :key="issue"
                >
                  <div class="inline-block px-3">
                    <div
                      class="md:h-[35vh] flex md:w-[12vw] rounded-lg ml-4 border-2 justify-center bg-cover items-center transition-shadow duration-300 ease-in-out"
                      :style="`background-image: ${'url(' + image + ')'}; border-color: rgb${themecolor}`"
                    > 
             <div
      class="h-full w-full justify-center items-center rounded-lg flex"
      :style="`background: rgba(25,18,43,0.7);`"
    >       <p
          class="md:text-xl text-white text-sm leading-none uppercase pb-2 break-words"
        >
          {{ issue.title }}
        </p></div>
        
                  </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>

<script setup>
import { onMounted, ref,reactive } from "vue";
import { useRoute } from "vue-router";
import HeaderItem from "../components/HeaderItem.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import TokenService from "../services/TokenService";

const headers = TokenService.getTokenHeader("");
const route = useRoute("");
const series = ref("");
const issues = ref("");
const themecolor = ref("");
const image = ref();
let Image = "noimage";

const props = defineProps({
  id: Number,
});

const issuestyle = reactive({
  borderColor: `rgb${themecolor}`,
  backgroundImage: `${'url(' + image + ')'}`
})

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
    issues.value = response.data.data;
    console.log(issues);
  } catch (error) {
    // message.value = error;
    console.log(error);
  }
}

onMounted(() => {
  getSeries(), getIssues();
});
</script>

<style scoped>
.hide-scroll-bar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.hide-scroll-bar::-webkit-scrollbar {
  display: none;
}
</style>
