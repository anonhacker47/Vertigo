<template>
  <div v-if="series" class="bg-no-repeat bg-center h-full bg-cover"
    :style="{ backgroundImage: 'url(' + image + ')' }">
    <div class="flex flex-col min-h-screen min-w-screen " style="background: rgba(18,25,43,0.95)">
      <HeaderItem />
      <div class="flex flex-col md:flex-row md:justify-between justify-center items-center py-4 px-4 border-b gap-4 border-slate-700 flex-wrap">
        <div class="flex flex-1 justify-center md:justify-start items-center px-5 md:w-1/3 break-words">
          <p class="font-bold text-3xl truncate" :style="`color: rgb${themecolor}`">
            {{ series.title }}
          </p>
        </div>
        <div class="flex flex-1 justify-center items-center md:w-1/4 gap-5">
          <div class="tooltip tooltip-success tooltip-bottom" data-tip="Number of Issues">
            <div class="flex flex-row items-center">
              <img class="" src="../assets/wishlist.svg" alt="" width="28" height="28" />
              <p class="pl-2 text-primary font-bold text-lg">
                {{ issueCount.total_count }}
              </p>
            </div>
          </div>
          <div class="tooltip tooltip-success tooltip-bottom" data-tip="Collected">
            <div class="flex flex-row items-center">
              <img src="../assets/collection.svg" alt="" width="28" height="28" />
              <p class="pl-2 text-primary font-bold text-lg">{{ issueCount.owned_count + "/" + issueCount.total_count }}
              </p>
            </div>
          </div>
          <div class="tooltip tooltip-success tooltip-bottom" data-tip="Read">
            <div class="flex flex-row items-center">
              <img src="../assets/read.svg" alt="" width="28" height="28" />
              <p class="pl-2 text-primary font-bold text-lg">{{ issueCount.read_count + "/" + issueCount.total_count }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-1 justify-center md:justify-end items-center w-1/3">
          <Rating :modelValue="series.user_rating" :cancel="false" :stars="5" />
        </div>
      </div>

      <div class="flex flex-col md:flex-row grow">
        <div class="flex flex-col mb-6 mr-2 md:basis-1/2 md:w-1/2 w-full">
          <div class="flex flex-col md:flex-row pt-8 basis-1/2 shrink-0 relative gap-4">
            <div class="flex flex-col basis-1/3 px-28 md:px-4">
              <img v-if="image != 'noimage'" :src="image" alt="" class="rounded-lg border-2"
                :style="`border-color: rgb${themecolor}`" @error="image = placeholder" />
              <div class="flex flex-row items-center justify-center gap-2 mt-2 px-2 py-1 rounded-sm bg-slate-800"
                :style="`border-color: rgb${themecolor}; color: rgb${themecolor}`">
                <p class="text-sm font-bold">
                  {{ series.series_format }}
                </p>
              </div>
            </div>
            <div class="flex flex-col basis-2/3 shrink-0 overflow-scroll gap-4">
              <div class="flex flex-col md:flex-row justify-center md:justify-start items-center gap-4">
                <span class=" font-bold text-lg">Publisher</span>
                <span class="text-sm font-bold bg-slate-800 rounded-md px-4 py-1" :style="`color: rgb${themecolor}`">{{ series.publisher }}</span>
              </div>
              <div class="flex flex-col md:flex-row justify-center md:justify-start items-center gap-4"> 
                <div class="font-bold text-lg">Genre</div>
                <div class="flex flex-row gap-4 max-w-md justify-center md:justify-start overflow-scroll whitespace-nowrap flex-wrap ">
                  <p v-for="genre in series.genre" class="bg-slate-800 rounded-md  px-4 py-1 text-sm font-bold " :style="`color: rgb${themecolor}`">
                    {{ genre }}
                  </p>
                </div>
              </div>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <span class="font-bold text-lg">Main Character/Team</span>
                <span class="text-sm font-bold bg-slate-800 rounded-md px-4 py-1" :style="`color: rgb${themecolor}`">{{ series.main_char }}</span>
              </div>
              <div class="flex flex-col md:flex-row items-center max-w-full gap-4 ">
                <div class="font-bold text-lg">Creators</div>
                <div class="flex flex-row gap-4 overflow-scroll whitespace-nowrap justify-center md:justify-start flex-wrap md:flex-no">
                  <p v-for="creator in series.creator" class="bg-slate-800 flex-shrink rounded-md px-4 h-7 py-1 text-sm font-bold" :style="`color: rgb${themecolor}`">
                    {{ creator }}
                  </p>
                </div>
              </div>
            
            

            </div>

            <RouterLink :to="{ name: 'EditSeries', params: { Link: series.slug, Id: series.id } }"
              class="absolute right-0 top-2 cursor-pointer w-7 h-7">
              <EditIcon class="w-7 h-7" :fill-color="`rgb${themecolor}`" />
            </RouterLink>


          </div>
          <div class="flex flex-col relative shrink-0">
            <div class="mx-8 my-5">
              <p class="text-xl text-center font-bold" :style="`color: rgb${themecolor}`">
                Description
              </p>
              <p class="mt-4 text-justify">{{ series.description }}</p>
            </div>
          </div>

        </div>
        <div class="flex flex-col w-full items-center justify-evenly md:basis-1/2 md:w-1/2 shrink-0 border-l border-slate-700 mb-6">
          <h1 class="flex justify-center pb-4 px-4 font-bold text-3xl" :style="`color: rgb${themecolor}`">
            Issues
          </h1>
          <div class="overflow-scroll h-full flex flex-row justify-center items-start w-full">
            <div class="flex flex-wrap flex-start items-start gap-10 md:px-16 px-12">
              <IssueCarditem :image="image" :themecolor="themecolor" :title="issue.title" :is_owned="issue.is_owned"
                :is_read="issue.is_read" v-for="issue in issuesList" @updateStatus="updateStatus(issue, $event)"
                :key="issue.id" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>

<script setup lang="ts">
import { onMounted, ref, reactive } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "../store/user";


import type { Series } from "@/types/series.types";
import type { Issue } from "@/types/issue.types";

import HeaderItem from "../components/HeaderItem.vue";
import IssueCarditem from "../components/cards/IssueCarditem.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import DetailCardItem from "../components/cards/DetailCardItem.vue";
import EditIcon from "../assets/EditIcon.vue";
import Rating from "primevue/rating";

const publisherUrl = new URL("../assets/paypal.png", import.meta.url).href;
const genreUrl = new URL("../assets/grid.png", import.meta.url).href;
const teamUrl = new URL("../assets/group.png", import.meta.url).href;

const userstore = useUserStore();

const route = useRoute();
const series = ref<Series | null>(null);
const issuesList = ref<Issue[]>([]);

const pagination = ref()

const updatedSeries = reactive({ value: series });;
const issueCount = ref({
  owned_count: 0,
  read_count: 0,
  total_count: 0,
});
const themecolor = ref<string | null>("(212, 222, 252)");
const image = ref<string | null>();
const placeholder = "https://upload.wikimedia.org/wikipedia/commons/c/cd/Placeholder_male_superhero_c.png"

async function getSeries() {
  try {
    const response = await SeriesService.getSeriesbyId(Number(route.params.Id))
    series.value = response;
    themecolor.value = response.dominant_color.slice(0, -1).toString() + response.dominant_color.slice(-1).toString();

    if (series.value) {
      image.value = `${SeriesService.getImagebyId(series.value.id)}?t=${Date.now()}`;
      console.log("getSeries", image.value);
    }

  } catch (error) {
    console.log(error);
  }
}

async function getIssues() {
  try {
    const result: any = await IssueService.fetchIssues(Number(route.params.Id), "title", "asc");
    issuesList.value = result.issuesList;
    pagination.value = result.pagination;
  } catch (error) {
    console.log(error);
  }
}


async function getIssueCount() {
  try {
    const response = await IssueService.getIssueCount(
      Number(route.params.Id),
    );
    issueCount.value = response.data;
    console.log(issueCount);
  } catch (error) {
    console.log(error);
  }
}

async function updateStatus(issue: { [x: string]: any; id: any; }, field: string | number) {
  issue[field] = !issue[field];
  try {
    const updateData = { [field]: issue[field] }; // Use square brackets to set dynamic property name
    const response = await IssueService.updateIssue(
      issue.id,
      updateData);
    console.log(response.data[field]);
    getIssueCount();
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
