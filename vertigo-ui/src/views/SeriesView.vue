<template>
  <div v-if="series" class="bg-no-repeat bg-center h-screen bg-cover" :style="{ backgroundImage: 'url(' + image + ')' }">
    <div class="flex flex-col min-h-screen min-w-screen " style="background: rgba(18,25,43,0.95)">
      <HeaderItem />
      <div class="flex justify-end items-center py-4 pr-20 border-b border-slate-700">
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Number of Issues">
          <div class="px-5 flex flex-row items-center">
            <img class="" src="../assets/wishlist.svg" alt="" width="28" height="28" />
            <p class="pl-2 text-primary font-bold text-lg">
              {{ issueCount.total_count }}
            </p>
          </div>
        </div>
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Collected">
          <div class="px-5 flex flex-row items-center">
            <img src="../assets/collection.svg" alt="" width="28" height="28" />
            <p class="ml-2 text-primary font-bold text-lg">{{ issueCount.owned_count + "/" + issueCount.total_count }}</p>
          </div>
        </div>
        <div class="tooltip tooltip-success tooltip-bottom" data-tip="Read">
          <div class="px-5 flex flex-row items-center">
            <img src="../assets/read.svg" alt="" width="28" height="28" />
            <p class="ml-2 text-primary font-bold text-lg">{{ issueCount.read_count + "/" + issueCount.total_count }}</p>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row grow">
        <div class="flex flex-col mb-6 mr-2 basis-1/2">
          <div class="flex flex-row pt-8 basis-1/2 relative">
            <div class="flex flex-col basis-1/4 pl-4 pr-4">
              <img v-if="image != 'noimage'" :src="image" alt="" class="w-40 h-[14.5rem;]  rounded-lg border-2"
                :style="`border-color: rgb${themecolor}`" @error="image = placeholder" />
            </div>
            <div class="flex flex-col basis-3/4">

              <span class="text-4xl font-bold text-ellipsis inlnie-block -nowrap overflow-clip"
                :style="`color: rgb${themecolor}`">
                {{ series.title }}
              </span>
              <p class="text-xl font-bold uppercase" :style="`color: rgb${themecolor}`">
                {{ series.publisher }}
              </p>
              <div class="flex flex-row flex-grow max-h-52 justify-around items-center">
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

            <RouterLink :to="{name: 'EditSeries', params: {Link: series.slug, Id: series.id}}" class="absolute right-0 top-2 cursor-pointer w-7 h-7">
              <EditIcon class="w-7 h-7" :fill-color="`rgb${themecolor}`" />
            </RouterLink>


          </div>
          <div class="flex flex-col basis-1/2 relative">
            <div class=" p-10">
              <p class="text-xl font-bold" :style="`color: rgb${themecolor}`">
                {{ "Description:" }}
              </p>
              <p class=" text-justify">{{ series.description }}</p>
            </div>
          </div>

        </div>
        <div class="flex flex-col basis-1/2 flex-grow border-l border-slate-700 pt-4 pb-6">
          <h1 class="flex pb-4 px-4 font-bold text-3xl" :style="`color: rgb${themecolor}`">
            Issues
          </h1>
          <div class="overflow-scroll" style="height: 70vh">
            <div class="grid grid-cols-4 gap-5 px-16">
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
import EditSeriesModal from "../components/modals/EditSeriesModal.vue";
import SingleSelectCombobox from "../components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "../components/customInputs/MultiSelectCombobox.vue";
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
    const result: any = await IssueService.fetchIssues( Number(route.params.Id), "title", "asc");
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
