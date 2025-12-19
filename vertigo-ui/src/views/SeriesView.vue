<template>
  <div v-if="series" :key="series.id" class="bg-no-repeat select-none bg-center bg-cover">
    <div class="flex flex-col md:h-[calc(100vh-72px)] w-full">
      <div
        class="flex flex-col md:flex-row md:justify-between justify-center items-center py-4 px-4 border-b gap-4 border-slate-700 flex-wrap">
        <div class="flex flex-1 justify-center md:justify-start items-center px-5 wrap-break-word">
          <div class="tooltip tooltip-success tooltip-bottom" :data-tip="series.title">
            <span :v-tooltip.bottom="series.title" :style="themecolor ? { color: `rgb${themecolor}` } : {}"
              class="font-bold xl:max-w-xl lg:max-w-md max-w-2xs block text-wrap md:text-nowrap text-center text-2xl md:truncate text-primary">
              {{ series.title }}
            </span>
          </div>
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
        <div class="md:hidden flex w-full flex-row justify-between ">
          <RouterLink v-if="neighbours.previous" :to="`/series/${neighbours.previous.id}-${neighbours.previous.slug}`"
            class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 flex gap-2 items-center"
            :style="`color: rgb${themecolor}`">
            <i class="pi pi-chevron-left"></i>
            <span>Previous Series </span>
          </RouterLink>

          <div v-else></div>

          <RouterLink v-if="neighbours.next" :to="`/series/${neighbours.next.id}-${neighbours.next.slug}`"
            class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 flex gap-2 items-center"
            :style="`color: rgb${themecolor}`">
            <span>Next Series </span>
            <i class="pi pi-chevron-right"></i>
          </RouterLink>

        </div>
      </div>

      <div class="flex flex-col md:flex-row overflow-hidden">
        <div class="flex flex-col relative pr-2 md:basis-1/2 justify-between md:w-1/2 w-full md:overflow-y-auto">
          <div class="flex flex-col md:flex-row pt-8 basis-1/2  relative gap-4">
            <div class="flex flex-col basis-1/3 px-28 h-fit md:px-4">
              <img v-if="image && image !== 'noimage'" :src="image" alt=""
                class="rounded-lg border-2 border-primary max-h-80 object-cover w-full h-full"
                :style="themecolor ? { borderColor: `rgb${themecolor}` } : {}" />

              <div v-else
                class="w-full border-2 rounded-lg h-full flex bg-slate-900 items-center justify-center p-4 text-center">
                <span class="text-4xl text-primary font-semibold opacity-70">
                  {{ series.title }}
                </span>
              </div>
              <RouterLink :to="{
                path: '/collection',
                query: { series_format: series.series_format }
              }"
                class="flex flex-row items-center justify-center gap-2 mt-2 px-2 py-1 rounded-smtext-slate-300 bg-slate-800"
                :style="`border-color: rgb${themecolor}; color: rgb${themecolor}`">
                <p class="text-sm font-bold">
                  {{ series.series_format }}
                </p>
              </RouterLink>
            </div>
            <div class="basis-2/3 shrink h-fit overflow-y-auto my-4">
              <table class="w-full border-collapse">
                <tbody class="flex md:block flex-col items-center justify-center">

                  <tr class="block md:table-row md:border-b md:border-slate-700/50">
                    <th
                      class="block md:table-cell md:py-4 md:pr-6  md:text-left text-sm uppercase tracking-wider text-slate-300">
                      Publisher
                    </th>
                    <td class="py-4 block md:table-cell">
                      <TagLink v-if="series.publisher" :label="series.publisher.title"
                        :to="`/publisher/${series.publisher.id}-${series.publisher.slug}`" :color="themecolor" />
                    </td>
                  </tr>

                  <tr class="block md:table-row md:border-b md:border-slate-700/50">
                    <th
                      class="block md:table-cell md:py-4 md:pr-6 md:text-left text-sm uppercase tracking-wider text-slate-300">
                      Genre
                    </th>
                    <td class="py-4">
                      <div class="flex flex-wrap gap-2">
                        <span v-for="genre in series.genre" :key="genre"
                          class="bg-slate-800 px-3 py-1 select-none rounded text-sm font-bold"
                          :style="`color: rgb${themecolor}`">
                          {{ genre }}
                        </span>
                      </div>
                    </td>
                  </tr>

                  <tr class="block md:table-row md:border-b border-slate-700/50">
                    <th
                      class="block md:table-cell md:py-4 md:pr-6 md:text-left text-sm uppercase tracking-wider text-slate-300">
                      Characters
                    </th>
                    <td class="py-4 block md:table-cell">
                      <div class="flex md:justify-start justify-center flex-wrap gap-2 max-h-36 overflow-y-auto">
                        <TagLink v-for="character in series.character" :key="character.id || character.title"
                          :label="character.title" :to="`/character/${character.id}-${character.slug}`"
                          :color="themecolor" />
                      </div>
                    </td>
                  </tr>

                  <tr class="block md:table-row md:border-b md:border-slate-700/50">
                    <th
                      class="block md:table-cell md:py-4 md:pr-6 md:text-left text-sm uppercase tracking-wider text-slate-300">
                      Creators
                    </th>
                    <td class="py-4 block md:table-cell">
                      <div class="flex md:justify-start justify-center flex-wrap gap-2 max-h-36 overflow-y-auto">
                        <TagLink v-for="creator in series.creator" :key="creator.id || creator.title"
                          :label="creator.title" :to="`/creator/${creator.id}-${creator.slug}`" :color="themecolor" />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
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
              <p class="text-xl text-center font-bold text-slate-300">
                Description
              </p>
              <p class="mt-4 text-justify" :style="`color: rgb${themecolor}`">
                {{ series.description }}
              </p>
            </div>

          </div>
          <div class="hidden md:flex w-full pl-2 flex-row justify-between mb-12">
            <RouterLink v-if="neighbours.previous" :to="`/series/${neighbours.previous.id}-${neighbours.previous.slug}`"
              class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 gap-2 items-center flex">
              <i class="pi pi-chevron-left"></i>
              <span>Previous Series</span>
            </RouterLink>

            <div v-else></div>

            <RouterLink v-if="neighbours.next" :to="`/series/${neighbours.next.id}-${neighbours.next.slug}`"
              class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 flex gap-2 items-center">
              <span>Next Series </span>
              <i class="pi pi-chevron-right"></i>
            </RouterLink>

          </div>
        </div>
        <div
          class="relative flex flex-col w-full items-center justify-evenly md:basis-1/2 md:w-1/2 shrink border-l border-slate-700">
          <h1 class="flex justify-center py-2 px-4 font-bold text-3xl text-slate-300">
            Issues
          </h1>
          <div class="md:overflow-scroll pb-12 h-full w-full">
            <div class="grid gap-y-8 md:px-20 place-items-center my-4 grid-cols-[repeat(auto-fill,minmax(176px,1fr))]">
              <IssueCard :edit_mode="editMode" :is_last="index === issuesList.length - 1 && issuesList.length > 1
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

import IssueCard from "../components/cards/IssueCard.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import EditIcon from "@/assets/EditIcon.vue";
import Rating from "primevue/rating";
import { useToast } from "primevue/usetoast";
import { useConfirmAction } from "@/composables/useConfirmAction";
import TagLink from "@/components/common/TagLink.vue";

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
      image.value = `${SeriesService.getSeriesImageById(series.value.id)}}`;
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
  } catch (error) {
    console.error("Failed to update rating:", error);
  }
}

async function getNeighbours(id: number) {
  const res = await SeriesService.getSeriesNeighbours(id);
  neighbours.value = res.data;
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
  if (!newImage) return;

  const app = document.querySelector('#app');
  if (!app) return;

  app.style.background = `
    linear-gradient(
      rgba(18, 25, 43, 0.92),
      rgba(18, 25, 43, 0.85)
    ),
    url(${newImage}) center / cover no-repeat fixed
  `;
});

onUnmounted(() => {
  const app = document.querySelector('#app');
  if (app) {
    app.style.background = '';
  }
});



</script>