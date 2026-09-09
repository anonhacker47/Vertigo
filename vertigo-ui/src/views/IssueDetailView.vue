<template>
  <div v-if="issue" :key="issue.id" class="bg-no-repeat select-none bg-center bg-cover">
    <div class="flex flex-col md:h-[calc(100vh-72px)] w-full">

      <div
        class="flex flex-col md:flex-row md:justify-between justify-center items-center py-4 px-4 border-b gap-4 border-slate-700 flex-wrap">

        <div class="flex md:w-1/3 justify-center md:justify-start items-center px-5 wrap-break-word">
          <div class="tooltip tooltip-success tooltip-bottom" :data-tip="issue.series.title + ' #' + issue.number">
            <span :style="themecolor ? { color: `rgb${themecolor}` } : {}"
              class="font-bold xl:max-w-xl lg:max-w-md max-w-2xs block text-wrap md:text-nowrap text-center text-2xl md:truncate text-primary">
              {{ issue.series.title }} #{{ issue.number }}
            </span>
          </div>
        </div>

        <div class="flex justify-center items-center md:w-1/4 gap-8 md:gap-5">
          <div class="w-1/2 md:w-fit tooltip tooltip-success tooltip-bottom" :data-tip="issue.is_owned ? 'Owned' : 'Not Owned'">
            <button @click="toggleStatus('is_owned')"
              class="flex flex-row items-center transition hover:scale-105 cursor-pointer">
              <img :class="{ 'opacity-40': !issue.is_owned }" src="../assets/collection.svg" alt="Owned" width="28"
                height="28" />
              <p class="pl-2 text-primary font-bold text-lg">
                {{ issue.is_owned ? 'Owned' : 'Missing' }}
              </p>
            </button>
          </div>

          <div class="w-1/2 md:w-fit  tooltip tooltip-success tooltip-bottom" :data-tip="issue.is_read ? 'Read' : 'Unread'">
            <button @click="toggleStatus('is_read')"
              class="flex flex-row items-center transition hover:scale-105 cursor-pointer">
              <img :class="{ 'opacity-40': !issue.is_read }" src="../assets/read.svg" alt="Read" width="28"
                height="28" />
              <p class="pl-2 text-primary font-bold text-lg">
                {{ issue.is_read ? 'Read' : 'Unread' }}
              </p>
            </button>
          </div>
        </div>

        <div class="flex w-1/3 justify-center md:justify-end items-center">
          <!-- <RouterLink 
            :to="`/series/${issue.series_id}-${issue.series.slug}/`" 
            class="text-sm font-bold border px-3 py-1 rounded bg-slate-800 border-slate-700 hover:bg-slate-700 transition"
            :style="`color: rgb${themecolor}`"
          >
            Back to Series
          </RouterLink> -->
          <Rating @update:model-value="updateRating" :modelValue="issue.user_rating" :cancel="false" :stars="5" />
        </div>
      </div>

      <div class="flex flex-col md:flex-row flex-1 overflow-hidden">

        <div class="flex flex-col md:flex-row py-8 flex-1 relative gap-4">

          <div class="flex flex-col px-28 md:max-w-xs h-fit md:px-4">
            <img v-if="image && image !== 'noimage'" :src="image" alt="Issue Cover"
              class="rounded-lg border-2 border-primary max-h-100 object-cover w-full h-full"
              :style="themecolor ? { borderColor: `rgb${themecolor}` } : {}" />
            <div v-else
              class="w-full border-2 rounded-lg h-96 flex bg-slate-900 items-center justify-center p-4 text-center">
              <span class="text-4xl text-primary font-semibold opacity-70">
                #{{ issue.number }}
              </span>
            </div>
            <div class="flex flex-col gap-2 mt-2">
              <RouterLink :to="{
                path: '/collection',
                query: { series_format: issue.series.series_format }
              }"
                class="flex flex-row items-center justify-center gap-2 px-2 py-1 rounded-sm text-slate-300 bg-slate-800"
                :style="`border-color: rgb${themecolor}; color: rgb${themecolor}`">
                <p class="text-sm font-bold">
                  {{ issue.series.series_format }}
                </p>
              </RouterLink>

              <a v-if="issue.metron_url" :href="issue.metron_url" target="_blank" rel="noopener noreferrer"
                class="flex flex-row items-center justify-center border border-slate-600 gap-2 px-2 py-1  rounded-sm text-slate-300 bg-slate-900 hover:bg-slate-700 transition"
                :style="`color: rgb${themecolor}`">
                <p class="text-sm font-semibold flex items-center gap-2">
                  View on Metron
                  <i class="pi pi-external-link text-sm"></i>
                </p>
              </a>
              <p v-if="issue.metron_id" class="mt-1 text-sm text-slate-400 text-center select-all">
                Metron ID: {{ issue.metron_id }}
              </p>
            </div>
          </div>

          <div class="h-full flex-1 overflow-y-auto px-4 flex flex-col gap-6">

            <div class="grid grid-cols-1 sm:grid-cols-5 gap-4">

              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Issue Title</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.title }}
                </span>
              </div>

              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Series</span>
                <RouterLink :to="{ path: `/series/${issue.series.id}-${issue.series.slug}` }"
                  class="text-sm font-medium hover:text-blue-300 hover:underline transition-colors truncate"
                  :style="`color: rgb${themecolor}`">
                  {{ issue.series.title }}
                </RouterLink>
              </div>

              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Bought Date</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.bought_date ? formatDate(issue.bought_date) : '' }}
                </span>
              </div>

              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Purchase Price</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.bought_price ? `${preferred_currency} ${issue.bought_price}` : '' }}
                </span>
              </div>

              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Read Date</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.read_date ? formatDate(issue.read_date) : '' }}
                </span>
              </div>
              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1 sm:col-span-3">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Description</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.description || 'No description available' }}
                </span>
              </div>
              <div class="p-3 bg-slate-950/40 rounded-lg border border-slate-800/40 flex flex-col gap-1 sm:col-span-2">
                <span class="text-sm font-bold text-slate-300 uppercase tracking-widest">Notes</span>
                <span class="text-sm font-medium text-slate-200" :style="`color: rgb${themecolor}`">
                  {{ issue.notes || 'No notes available' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <PurchaseConfirmModal :show="showPriceModal" :currency="preferred_currency" :initial-price="issue?.bought_price"
    :initial-date="issue?.bought_date" @cancel="cancelPriceModal" @confirm="confirmPriceAndUpdate" />

  <ReadConfirmModal :show="showReadModal" :initial-date="issue?.read_date" @cancel="cancelReadModal"
    @confirm="confirmReadAndUpdate" />

</template>

<script setup lang="ts">
import { onMounted, ref, reactive, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "../store/user.js";
import { useToast } from "primevue/usetoast";
import IssueService from "../services/IssueService.js";
import SeriesService from "../services/SeriesService.js";
import { Issue } from "@/types/issue.types.js";
import Rating from "primevue/rating";
import PurchaseConfirmModal from "@/components/modals/PurchaseConfirmModal.vue";
import ReadConfirmModal from "@/components/modals/ReadConfirmModal.vue";

const route = useRoute();
const toast = useToast();

// 1. Properly parse our reactive route params
const seriesId = Number(route.params.seriesId as string);
const issueNumber = Number(route.params.number as string);

const showPriceModal = ref(false);
const showReadModal = ref(false);
const { preferred_currency } = useUserStore().getUser();

const issue = ref<Issue | null>(null);
const themecolor = ref<string | null>(null);
const image = ref<string | null>(null);

const editForm = reactive({
  bought_price: null as number | null,
  bought_date: "",
  read_date: "",
});

// 2. Removed the unused 'id' argument since we use seriesId and issueNumber from the outer scope
async function getIssueDetails() {
  try {
    const response = await IssueService.getIssue(seriesId, issueNumber);
    issue.value = response.data;

    if (!issue.value) return;

    editForm.bought_price = issue.value.bought_price;
    editForm.bought_date = issue.value.bought_date?.substring(0, 10) || "";
    editForm.read_date = issue.value.read_date?.substring(0, 10) || "";

    const parent = issue.value.series;
    if (parent) {
      themecolor.value = parent.dominant_color;
      image.value = parent.thumbnail ? `${SeriesService.getSeriesImageById(parent.id, parent.last_updated)}` : null;
    }
  } catch (error) {
    console.error("Error fetching issue details:", error);
  }
}

async function toggleStatus(field: 'is_owned' | 'is_read') {
  if (!issue.value) return;
  const targetValue = !issue.value[field];

  if (field === 'is_owned' && targetValue) {
    showPriceModal.value = true;
    return;
  }

  if (field === 'is_read' && targetValue) {
    showReadModal.value = true;
    return;
  }

  if (field === 'is_owned' && !targetValue) {
    try {
      await IssueService.updateIssue(issue.value.id, { bought_price: null, bought_date: null });
      editForm.bought_price = null;
      editForm.bought_date = "";
    } catch (e) {
      console.error(e);
    }
  }

  await submitValueUpdate(field, targetValue);
}

function cancelPriceModal() {
  showPriceModal.value = false;
}

async function confirmPriceAndUpdate(payload: { price: number | null; date: string | null }) {
  if (!issue.value) return;
  showPriceModal.value = false;

  try {
    await IssueService.updateIssue(issue.value.id, {
      bought_price: payload.price,
      bought_date: payload.date,
      is_owned: 1
    });

    editForm.bought_price = payload.price;
    editForm.bought_date = payload.date ? payload.date.substring(0, 10) : "";

    toast.add({ 
      severity: "success", 
      summary: "Updated", 
      detail: "Issue added to collection.", 
      life: 2000 
    });

    getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Log Update Failed", detail: String(error), life: 3000 });
  }
}

function cancelReadModal() {
  showReadModal.value = false;
}

async function confirmReadAndUpdate(payload: { date: string | null }) {
  if (!issue.value) return;
  showReadModal.value = false;

  try {
    await IssueService.updateIssue(issue.value.id, {
      is_read: true,
      read_date: payload.date
    });

    editForm.read_date = payload.date ? payload.date.substring(0, 10) : "";

    toast.add({
      severity: "success",
      summary: "Updated",
      detail: "Issue marked as read.",
      life: 2000
    });

    getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Update Failed", detail: String(error), life: 3000 });
  }
}

async function submitValueUpdate(field: string, value: any) {
  if (!issue.value) return;
  try {
    const exactValue = (field === 'bought_date' || field === 'read_date') && value
      ? new Date(value).toISOString()
      : value;

    await IssueService.updateIssue(issue.value.id, { [field]: exactValue });

    toast.add({ severity: "success", summary: "Updated", detail: `${field.replace('_', ' ')} updated.`, life: 2000 });
    
    // 3. Updated this callback line to match the parameterless function signature
    getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Update Failed", detail: String(error), life: 3000 });
  }
}

const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });

watch(
  () => [route.params.seriesId, route.params.number], 
  () => getIssueDetails()
);

onMounted(() => {
  getIssueDetails();
});

watch(image, (newImage) => {
  const app = document.querySelector('#app') as HTMLElement;
  if (app) app.style.background = newImage ? `linear-gradient(rgba(18, 25, 43, 0.94), rgba(18, 25, 43, 0.88)), url(${newImage}) center / cover no-repeat fixed` : '';
});

onUnmounted(() => {
  const app = document.querySelector('#app') as HTMLElement;
  if (app) app.style.background = '';
});

async function updateRating(newRating: number) {
  try {
    const formData = new FormData();
    formData.append("user_rating", String(newRating));

    await IssueService.updateIssue(issue.value.id, formData); 
    await getIssueDetails(); 
  } catch (error) {
    console.error("Failed to update rating:", error);
  }
}
</script>