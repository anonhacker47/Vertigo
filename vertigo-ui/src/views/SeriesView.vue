<template>
  <div v-if="series" :key="series.id" class="bg-no-repeat bg-center bg-cover h-full">
    <div class="flex flex-col min-w-screen" style="background: rgba(18, 25, 43, 0.9)">
      <div
        class="flex flex-col md:flex-row md:justify-between justify-center items-center py-4 px-4 border-b gap-4 border-slate-700 flex-wrap">
        <div class="flex flex-1 justify-center md:justify-start items-center px-5 md:w-1/3 break-words">
          <p :style="themecolor ? { color: `rgb${themecolor}` } : {}" class="font-bold text-3xl truncate text-primary">
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
              <p class="pl-2 text-primary font-bold text-lg">
                {{ issueCount.owned_count + "/" + issueCount.total_count }}
              </p>
            </div>
          </div>
          <div class="tooltip tooltip-success tooltip-bottom" data-tip="Read">
            <div class="flex flex-row items-center">
              <img src="../assets/read.svg" alt="" width="28" height="28" />
              <p class="pl-2 text-primary font-bold text-lg">
                {{ issueCount.read_count + "/" + issueCount.total_count }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-1 justify-center md:justify-end items-center w-1/3">
          <Rating @update:model-value="updateRating" :modelValue="series.user_rating" :cancel="false" :stars="5" />
        </div>
      </div>

      <div class="flex flex-col md:flex-row grow h-[86vh]">
        <div class="flex flex-col relative mr-2 md:basis-1/2 md:w-1/2 w-full overflow-hidden">
          <div class="flex flex-col md:flex-row pt-8 basis-1/2 shrink-0 relative gap-4">
            <div class="flex flex-col basis-1/3 px-28 md:px-4">
              <img v-if="image && image !== 'noimage'" :src="image" alt=""
                class="rounded-lg border-2 border-primary max-h-96 object-cover w-full h-full"
                :style="themecolor ? { borderColor: `rgb${themecolor}` } : {}" />

              <!-- Fallback title block -->
              <div v-else
                class="w-full border-2 rounded-lg h-full flex bg-slate-900 items-center justify-center p-4 text-center">
                <span class="text-4xl text-primary font-semibold opacity-70">
                  {{ series.title }}
                </span>
              </div>
              <div class="flex flex-row items-center justify-center gap-2 mt-2 px-2 py-1 rounded-sm bg-slate-800"
                :style="`border-color: rgb${themecolor}; color: rgb${themecolor}`">
                <p class="text-sm font-bold">
                  {{ series.series_format }}
                </p>
              </div>
            </div>
            <div class="flex flex-col basis-2/3 shrink-0 overflow-scroll gap-4">
              <div class="flex flex-col md:flex-row justify-center md:justify-start items-center gap-4">
                <span class="font-bold text-lg">Publisher</span>
                <span class="text-sm font-bold bg-slate-800 rounded-md px-4 py-1" :style="`color: rgb${themecolor}`">{{

                  series.publisher }}</span>
              </div>
              <div class="flex flex-col md:flex-row justify-center md:justify-start items-center gap-4">
                <div class="font-bold text-lg">Genre</div>
                <div
                  class="flex flex-row gap-4 max-w-md justify-center md:justify-start overflow-scroll whitespace-nowrap flex-wrap">
                  <p v-for="genre in series.genre" class="bg-slate-800 rounded-md px-4 py-1 text-sm font-bold"
                    :style="`color: rgb${themecolor}`">
                    {{ genre }}
                  </p>
                </div>
              </div>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <span class="font-bold text-lg">Characters</span>
                <div
                  class="flex flex-row gap-4 max-w-md justify-center md:justify-start overflow-scroll whitespace-nowrap flex-wrap">
                  <p v-for="character in series.character" class="bg-slate-800 rounded-md px-4 py-1 text-sm font-bold"
                    :style="`color: rgb${themecolor}`">
                    {{ character }}
                  </p>
                </div>
              </div>
              <div class="flex flex-col md:flex-row items-center max-w-full gap-4">
                <div class="font-bold text-lg">Creators</div>
                <div
                  class="flex flex-row gap-4 overflow-scroll whitespace-nowrap justify-center md:justify-start flex-wrap md:flex-no">
                  <p v-for="creator in series.creator"
                    class="bg-slate-800 flex-shrink rounded-md px-4 h-7 py-1 text-sm font-bold"
                    :style="`color: rgb${themecolor}`">
                    {{ creator }}
                  </p>
                </div>
              </div>
            </div>

            <RouterLink :to="{
              name: 'EditSeries',
              params: { Link: series.slug, Id: series.id },
            }"
              class="absolute right-0 top-2 cursor-pointer w-12 h-12 transition duration-200 ease-in-out hover:scale-110 hover:border-emerald-400 hover:border-2 rounded-full flex items-center justify-center">
              <EditIcon class="w-7 h-7 fill-slate-300" :fill-color="`rgb${themecolor}`" />
            </RouterLink>
          </div>
          <div class="flex flex-col relative shrink-0">
            <div class="mx-8 my-5">
              <p class="text-xl text-center font-bold" :style="`color: rgb${themecolor}`">
                Description
              </p>
              <p class="mt-4 text-white text-justify">
                {{ series.description }}
              </p>
            </div>

          </div>
          <div class="flex absolute w-full pl-2 bottom-4 flex-row justify-between mt-6">
            <!-- Previous Button -->
            <RouterLink v-if="neighbours.previous" :to="`/series/${neighbours.previous.id}-${neighbours.previous.slug}`"
              class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition"
              :style="`color: rgb${themecolor}`">
              ← Previous Series
            </RouterLink>

            <!-- Spacer when no previous -->
            <div v-else></div>

            <!-- Next Button -->
            <RouterLink v-if="neighbours.next" :to="`/series/${neighbours.next.id}-${neighbours.next.slug}`"
              class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition"
              :style="`color: rgb${themecolor}`">
              Next Series →
            </RouterLink>

          </div>
        </div>
        <div
          class="relative flex flex-col w-full items-center justify-evenly md:basis-1/2 md:w-1/2 shrink-0 border-l border-slate-700">
          <h1 class="flex justify-center py-2 px-4 font-bold text-3xl" :style="`color: rgb${themecolor}`">
            Issues
          </h1>
          <div class="overflow-scroll h-full flex flex-row justify-center mx-auto items-start w-full">
            <div class="flex flex-wrap flex-start gap-10 w-[82%] my-4 ">
              <IssueCarditem :edit_mode="editMode" :is_last="index === issuesList.length - 1 && issuesList.length > 1
                " :preferred_currency="preferred_currency" :bought_price="issue.bought_price" :image="image"
                :bought_date="issue.bought_date" :read_date="issue.read_date" :themecolor="themecolor"
                :title="issue.title" :is_owned="issue.is_owned" :is_read="issue.is_read"
                v-for="(issue, index) in issuesList" @updateStatus="updateStatus(issue, $event)" :key="issue.id"
                @deleteIssue="confirmDelete(issue)" />

              <div v-if="editMode" @click="addIssue"
                class="w-44 h-64 flex relative flex-col items-center bg-cover bg-center justify-center rounded-lg border-green-500 border-2 overflow-hidden shadow-lg cursor-pointer bg-zinc-800 border-dashed hover:bg-zinc-700 transition-all"
                :style="`background-image: url(${image})`">
                <div class="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center px-3">
                  <div class="flex flex-col items-center justify-center text-white gap-2">
                    <img src="@/assets/add.svg" alt="Add" class="w-12 h-12 opacity-80" />
                    <p class="text-white text-md font-bold">Add Issue</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button @click="toggleEditMode"
            class="mt-4 absolute right-2 -top-2 w-12 h-12 cursor-pointer hover:scale-110 rounded-full transition duration-200 ease-in-out hover:border-emerald-400 hover:border-2 flex items-center justify-center"
            :class="editMode ? ' border-green-700' : ' border-zinc-500'">
            <EditIcon class="w-7 h-7" :fill="editMode ? 'white' : `rgb${themecolor}`" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive, watch, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "../store/user";

import type { Series } from "@/types/series.types";
import type { Issue } from "@/types/issue.types";

import IssueCarditem from "../components/cards/IssueCarditem.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import EditIcon from "@/assets/EditIcon.vue";
import Rating from "primevue/rating";
import { useToast } from "primevue/usetoast";
import { useConfirmAction } from "@/composables/useConfirmAction";

const { confirmAction } = useConfirmAction();
const toast = useToast();

const message = ref();
const neighbours = ref({ next: null, previous: null });

async function addIssue() {
  try {
    const response = await IssueService.createIssue(Number(route.params.Id));
    getIssues();
    getIssueCount();
    toast.add({
      severity: "success",
      summary: "Success",
      detail: `Issue ${response.data.title} added`,
      life: 3000,
    });
  } catch (error) {
    message.value = error;
    toast.add({
      severity: "error",
      summary: "Error",
      detail: message.value,
      life: 3000,
    });
  }
}

async function deleteIssue(issueToDelete: Issue) {
  try {
    const response = await IssueService.removeIssue(issueToDelete.id);
    getIssues();
    getIssueCount();
  } catch (error) {
    message.value = error;
    toast.add({
      severity: "error",
      summary: "Error",
      detail: message.value,
      life: 3000,
    });
  }
}

const confirmDelete = (issue: Issue) => {
  confirmAction({
    message: `Issue ${issue.title}`,
    header: "Confirm Deletion",
    acceptLabel: "Delete",
    severity: "danger",
    successMessage: `${issue.title} deleted`,
    onAccept: () => deleteIssue(issue),
  });
};

const toggleEditMode = (): void => {
  editMode.value = !editMode.value;
  console.log("ediotMode", editMode.value);
};

const userstore = useUserStore();

const { preferred_currency: preferred_currency } = userstore.getUser();

const route = useRoute();
const series = ref<Series | null>(null);
const issuesList = ref<Issue[]>([]);

const pagination = ref();
const editMode = ref(false);

const updatedSeries = reactive({ value: series });
const issueCount = ref({
  owned_count: 0,
  read_count: 0,
  total_count: 0,
});
const themecolor = ref<string | null>(null);
const image = ref<string | null>(null);

async function getSeries(id: number) {
  try {
    const response = await SeriesService.getSeriesbyId(id);
    series.value = response;
    if (response.dominant_color) {
      themecolor.value =
        response.dominant_color.slice(0, -1).toString() +
        response.dominant_color.slice(-1).toString();
    }

    if (response.thumbnail) {
      image.value = `${SeriesService.getSeriesImageById(series.value.id)}?t=${Date.now()}`;
      console.log("getSeries", image.value);
    }
  } catch (error) {
    console.log(error);
  }
}

async function getIssues() {
  try {
    const result: any = await IssueService.fetchIssues(
      Number(route.params.Id),
      "title",
      "asc",
    );
    issuesList.value = result.issuesList;
    issuesList.value = issuesList.value.map((issue) => ({
      ...issue,
      bought_date: issue.bought_date ? new Date(issue.bought_date) : null,
      read_date: issue.read_date ? new Date(issue.read_date) : null,
    }));
    pagination.value = result.pagination;
  } catch (error) {
    console.log(error);
  }
}

async function getIssueCount() {
  try {
    const response = await IssueService.getIssueCount(Number(route.params.Id));
    issueCount.value = response.data;
    console.log(issueCount);
  } catch (error) {
    console.log(error);
  }
}

async function updateStatus(
  issue: { [x: string]: any; id: any },
  payload: { status: string; value: boolean; date?: string },
) {
  const { status, value, date } = payload;

  issue[status] = value;
  if (date) {
    const dateField = status === "is_owned" ? "bought_date" : "read_date";
    issue[dateField] = date;
  }

  try {
    const updateData: any = { [status]: value };
    if (date) {
      const dateField = status === "is_owned" ? "bought_date" : "read_date";
      const isoDate = new Date(date).toISOString();
      updateData[dateField] = isoDate;
    }

    const response = await IssueService.updateIssue(issue.id, updateData);
    console.log(response.data);
    getIssueCount();
  } catch (error) {
    console.log(error);
  }
}

async function updateRating(newRating: number) {
  try {
    const formData = new FormData();
    formData.append("user_rating", String(newRating));

    await SeriesService.updateSeries(Number(route.params.Id), formData); // or use a PATCH method if available
    await getSeries(Number(route.params.Id)); // re-fetch the full series data to reflect the change
    console.log("Rating updated and series reloaded.");
  } catch (error) {
    console.error("Failed to update rating:", error);
  }
}

async function getNeighbours(id: number) {
  const res = await SeriesService.getSeriesNeighbours(id);
  neighbours.value = res.data;
  console.log(res)
}

watch(
  () => route.params.Id,
  (newId) => {
    image.value = null;      // clear old image
    series.value = null;
    themecolor.value = null;
    getSeries(Number(newId));
    getIssues();
    getIssueCount();
    getNeighbours(Number(newId));
  }
);

onMounted(() => {
  getSeries(Number(route.params.Id));
  getIssues();
  getIssueCount();
  getNeighbours(Number(route.params.Id));
});

watch(image, (newImage) => {
  if (newImage) {
    const app = document.querySelector('#app');
    if (app) {
      app.style.background = `url(${newImage}) center/cover no-repeat fixed`;
    }
  }
});

onUnmounted(() => {
  const app = document.querySelector('#app');
  if (app) {
    app.style.background = '';
  }
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
