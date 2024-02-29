<template>
  <div class="top-0 right-0 bottom-0 left-0 bg-no-repeat bg-center bg-cover"
    :style="{ backgroundImage: 'url(' + image + ')' }">
    <div class="flex flex-col min-h-screen min-w-screen " style="background: rgba(18,25,43,0.95)">
      <HeaderItem />

      <div class="flex justify-end items-center py-4 pr-20 border-b border-slate-700">
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Number of Issues">
          <div class="px-5 flex flex-row items-center">
            <img class="" src="../assets/collection.svg" alt="" width="28" height="28" />
            <p class="pl-2 text-primary font-bold text-lg">
              {{ issueCount.total_count }}
            </p>
          </div>
        </div>
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Collected">
          <div class="px-5 flex flex-row items-center">
            <img src="../assets/cart.svg" alt="" width="23" height="23" />
            <!-- <div class="radial-progress text-accent ml-2" style="--value:66; --size:2.5rem;" role="progressbar"> -->
            <p class="ml-2 text-primary font-bold text-lg">{{ issueCount.have_count + "/" + issueCount.total_count }}</p>
            <!-- </div> -->
          </div>
        </div>
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Read">
          <div class="px-5 flex flex-row items-center">
            <img src="../assets/read.svg" alt="" width="25" height="25" />
            <!-- <div class="radial-progress text-warning ml-2" style="--value:100; --size:2.5rem" role="progressbar"> -->
            <p class="ml-2 text-primary font-bold text-lg">{{ issueCount.read_count + "/" + issueCount.total_count }}</p>
            <!-- </div> -->
          </div>
        </div>
      </div>

      <div class="flex flex-row grow">
        <div class="flex flex-row pb-6 pr-7 basis-1/2">
          <div class="flex flex-row">

            <img v-if="image != Image" :src="image" alt="" class="md:h-[45vh] md:w-[15vw] rounded-lg mt-8 ml-16 border-2"
              :style="`border-color: rgb${themecolor}`" @error="image = Image" />
            <div class="flex flex-col mt-8 ml-8">
              <p class="text-5xl font-bold" :style="`color: rgb${themecolor}`">
                {{ series.title }}
              </p>
              <p class="text-xl font-bold uppercase" :style="`color: rgb${themecolor}`">
                {{ series.publisher }}
              </p>
              <p class="text-base text-white mt-4 font-normal" :style="`color: rgb${themecolor}`">
                {{ series.summary }}
              </p>
              <div class="flex flex-row flex-grow justify-around items-center">
                <!-- Column 1 -->
                <div class="flex flex-col align-middle self-center h-full justify-around items-start">
                  <DetailCardItem :icon="publisherUrl" field="Publisher" :detail="series.publisher" />
                  <DetailCardItem :icon="genreUrl" field="Genre" :detail="series.genre" />
                </div>

                <!-- Column 2 -->
                <div class="flex flex-col align-middle h-full justify-around items-start">
                  <DetailCardItem :icon="teamUrl" field="Main Character/Team" :detail="series.main_char" />
                  <DetailCardItem :icon="teamUrl" field="Writer" :detail="series.writer" />
                </div>

                <!-- Column 3 -->
                <div class="flex flex-col align-middle h-full justify-around items-start">
                  <DetailCardItem :icon="teamUrl" field="Artist" :detail="series.artist" />
                  <DetailCardItem :icon="teamUrl" field="Editor" :detail="series.editor" />
                </div>
              </div>

            </div>
          </div>
        </div>
        <div class="flex flex-col overflow-hidden flex-grow border-l border-slate-700 pt-4 pb-6">
          <h1 class="flex pb-4 px-4 font-bold text-3xl" :style="`color: rgb${themecolor}`">
            Issues
          </h1>
          <div class="overflow-scroll" style="height: 65vh;">
            <div class="grid grid-cols-4 gap-5 px-16">
              <!-- <div class="flex flex-row justify-center items-start" > -->
              <IssueCarditem :image="image" :themecolor="themecolor" :title="issue.title" v-for="issue in issues"
                :key="issue" />
              <!-- </div> -->
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
import IssueCarditem from "../components/cards/IssueCarditem.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import TokenService from "../services/TokenService";
import DetailCardItem from "../components/cards/DetailCardItem.vue";

const publisherUrl = new URL("../assets/paypal.png", import.meta.url).href;
const genreUrl = new URL("../assets/grid.png", import.meta.url).href;
const teamUrl = new URL("../assets/group.png", import.meta.url).href;

const headers = TokenService.getTokenHeader("");
const route = useRoute("");
const series = ref("");
const issues = ref("");
const issueCount = ref("");
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
    console.log(error);
  }
}


async function getIssueCount() {
  try {
    const response = await IssueService.getIssueCount(
      route.params.Id,
    );
    issueCount.value = response.data;
    console.log(issueCount);
  } catch (error) {
    console.log(error);
  }
}


onMounted(() => {
  getSeries(), getIssues(), getIssueCount();
});
</script>

<style scoped>
/* .hide-scroll-bar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.hide-scroll-bar::-webkit-scrollbar {
  display: none;
} */
</style>
