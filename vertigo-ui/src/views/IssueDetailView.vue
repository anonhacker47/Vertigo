<template>
  <div v-if="issue" :key="issue.id" class="select-none">
    <div class="flex flex-col md:h-[calc(100vh-72px)] w-full">

      <!-- Run navigation: previous issue | series + position | next issue -->
      <nav class="hidden md:grid grid-cols-[1fr_auto_1fr] items-center gap-4 px-6 py-3 border-b border-slate-800/60 text-sm">
        <RouterLink v-if="neighbours?.previous" :to="issueRoute(neighbours.previous.number)" title="Previous issue"
          class="justify-self-start flex items-center gap-2 min-w-0 max-w-full px-3 py-1.5 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition">
          <i class="pi pi-chevron-left text-xs"></i>
          <span class="truncate">{{ issueDisplayLabel(neighbours.previous.title, neighbours.previous.number) }}</span>
        </RouterLink>
        <span v-else></span>

        <div class="flex items-center gap-3 text-slate-400">
          <RouterLink :to="seriesRoute" class="font-semibold hover:underline" :style="accentStyle">
            {{ issue.series.title }}
          </RouterLink>
          <span v-if="neighbours?.total">{{ neighbours.position }} of {{ neighbours.total }}</span>
        </div>

        <RouterLink v-if="neighbours?.next" :to="issueRoute(neighbours.next.number)" title="Next issue"
          class="justify-self-end flex items-center gap-2 min-w-0 max-w-full px-3 py-1.5 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition">
          <span class="truncate">{{ issueDisplayLabel(neighbours.next.title, neighbours.next.number) }}</span>
          <i class="pi pi-chevron-right text-xs"></i>
        </RouterLink>
        <span v-else></span>
      </nav>

      <div class="flex flex-col md:flex-row flex-1 md:overflow-hidden gap-8 md:gap-10 px-6 md:px-10 py-6 md:py-8">

        <!-- Cover -->
        <div class="flex flex-col shrink-0 w-full max-w-xs mx-auto md:mx-0 md:w-72">
          <div class="relative w-full">
            <img v-if="image && image !== 'noimage'" :src="image" alt="Issue Cover"
              class="rounded-lg border-2 border-primary object-cover w-full" :style="accentBorderStyle" />
            <div v-else
              class="w-full border-2 border-primary rounded-lg aspect-[2/3] flex bg-slate-900 items-center justify-center p-4 text-center"
              :style="accentBorderStyle">
              <span class="text-4xl font-semibold opacity-70" :style="accentStyle">#{{ issue.number }}</span>
            </div>
            <button type="button" @click="showCoverModal = true" title="Change cover"
              class="absolute top-2 right-2 flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-200 bg-slate-950/80 border border-slate-700 backdrop-blur-sm hover:bg-slate-800 hover:text-white transition cursor-pointer">
              <i class="pi pi-image text-xs"></i>
              <span>Change cover</span>
            </button>
          </div>

          <div class="flex flex-col gap-2 mt-3 w-full">
            <a v-if="issue.metron_url" :href="issue.metron_url" target="_blank" rel="noopener noreferrer"
              class="flex flex-row items-center justify-center border border-slate-600 gap-2 px-2 py-1 rounded-sm text-slate-300 bg-slate-900 hover:bg-slate-700 transition"
              :style="accentStyle">
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

        <!-- Title, status, prose -->
        <div class="flex-1 min-w-0 md:overflow-y-auto flex flex-col gap-6 pr-1">
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <h1 class="font-bold leading-tight text-2xl md:text-3xl text-primary break-words" :style="accentStyle">
                <span class="font-medium opacity-80" :class="hasCustomTitle ? 'text-xl md:text-2xl mr-3' : ''">
                  #{{ issue.number }}
                </span>
                <span v-if="hasCustomTitle">{{ issue.title }}</span>
              </h1>
              <div class="flex flex-wrap items-center gap-2 mt-3 text-sm text-slate-300">
                <TagLink :label="issue.series.title" :to="seriesRoute" :color="themecolor || '(255,255,255)'" />
                <TagLink v-if="issue.series.series_format" :label="issue.series.series_format"
                  :to="{ path: '/collection', query: { series_format: issue.series.series_format } }"
                  :color="themecolor || '(255,255,255)'" />
                <span v-if="issue.cover_date" class="text-slate-400">Cover date {{ formatMonth(issue.cover_date) }}</span>
              </div>
            </div>

            <div class="tooltip tooltip-success tooltip-left shrink-0" data-tip="Edit Issue">
              <RouterLink :to="editRoute"
                class="flex items-center justify-center w-10 h-10 rounded-full transition duration-200 ease-in-out hover:scale-110 hover:border-2 hover:border-emerald-400">
                <EditIcon class="w-6 h-6" :fill-color="themecolor ? `rgb${themecolor}` : 'rgb(203, 213, 225)'" />
              </RouterLink>
            </div>
          </div>

          <!-- Status: the chips are the toggles -->
          <div class="flex flex-col gap-3">
            <div class="flex flex-wrap items-center gap-3">
              <button type="button" @click="toggleStatus('is_owned')"
                :title="issue.is_owned ? 'Remove from collection' : 'Mark as owned'"
                class="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg border transition cursor-pointer"
                :class="issue.is_owned
                  ? 'border-slate-600 bg-slate-800/70 text-white hover:bg-slate-800'
                  : 'border-dashed border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-500'">
                <img :class="{ 'opacity-40': !issue.is_owned }" src="../assets/collection.svg" alt="" width="22" height="22" />
                <span class="font-semibold">{{ issue.is_owned ? 'Owned' : 'Not owned' }}</span>
                <span v-if="issue.is_owned && issue.bought_date" class="text-slate-400">{{ formatDate(issue.bought_date) }}</span>
              </button>

              <button type="button" @click="toggleStatus('is_read')"
                :title="issue.is_read ? 'Mark as unread' : 'Mark as read'"
                class="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg border transition cursor-pointer"
                :class="issue.is_read
                  ? 'border-slate-600 bg-slate-800/70 text-white hover:bg-slate-800'
                  : 'border-dashed border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-500'">
                <img :class="{ 'opacity-40': !issue.is_read }" src="../assets/read.svg" alt="" width="22" height="22" />
                <span class="font-semibold">{{ issue.is_read ? 'Read' : 'Unread' }}</span>
                <span v-if="issue.is_read && issue.read_date" class="text-slate-400">{{ formatDate(issue.read_date) }}</span>
              </button>

              <span v-if="issue.is_owned && issue.bought_price !== null && issue.bought_price !== undefined"
                class="text-sm text-slate-300">
                Paid {{ currencySymbol }}{{ issue.bought_price }}
              </span>
            </div>

            <Rating @update:model-value="updateRating" :modelValue="issue.user_rating" :cancel="false" :stars="5" />
          </div>

          <section class="max-w-prose">
            <h2 class="text-sm font-semibold text-slate-300 mb-1.5">Description</h2>
            <p v-if="issue.description" class="text-sm md:text-base leading-relaxed text-slate-200 whitespace-pre-line">
              {{ issue.description }}
            </p>
            <p v-else class="text-sm text-slate-400">
              No description yet.
            </p>
          </section>

          <section class="max-w-prose">
            <h2 class="text-sm font-semibold text-slate-300 mb-1.5">Notes</h2>
            <p v-if="issue.notes" class="text-sm md:text-base leading-relaxed text-slate-200 whitespace-pre-line">
              {{ issue.notes }}
            </p>
            <p v-else class="text-sm text-slate-400">
              No notes yet.
            </p>
          </section>
        </div>
      </div>

      <!-- Run navigation on small screens -->
      <nav v-if="neighbours?.previous || neighbours?.next" class="md:hidden flex justify-between gap-3 px-6 pb-8">
        <RouterLink v-if="neighbours?.previous" :to="issueRoute(neighbours.previous.number)"
          class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 flex gap-2 items-center min-w-0"
          :style="accentStyle">
          <i class="pi pi-chevron-left"></i>
          <span class="truncate">{{ issueNumberLabel(neighbours.previous.number) }}</span>
        </RouterLink>
        <div v-else></div>

        <RouterLink v-if="neighbours?.next" :to="issueRoute(neighbours.next.number)"
          class="px-4 py-2 bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition text-slate-300 flex gap-2 items-center min-w-0"
          :style="accentStyle">
          <span class="truncate">{{ issueNumberLabel(neighbours.next.number) }}</span>
          <i class="pi pi-chevron-right"></i>
        </RouterLink>
      </nav>
    </div>
  </div>

  <PurchaseConfirmModal :show="showPriceModal" :currency="currencySymbol" :initial-price="issue?.bought_price"
    :initial-date="issue?.bought_date" @cancel="cancelPriceModal" @confirm="confirmPriceAndUpdate" />

  <ReadConfirmModal :show="showReadModal" :initial-date="issue?.read_date" @cancel="cancelReadModal"
    @confirm="confirmReadAndUpdate" />

  <IssueCoverModal :show="showCoverModal" :current-image="image" :has-own-cover="!!issue?.thumbnail"
    :busy="coverSaving" @cancel="showCoverModal = false" @save="saveIssueCover" @remove="removeIssueCover" />

</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "../store/user.js";
import { useToast } from "primevue/usetoast";
import IssueService from "../services/IssueService.js";
import SeriesService from "../services/SeriesService.js";
import type { Issue, IssueNeighbours } from "@/types/issue.types.js";
import Rating from "primevue/rating";
import PurchaseConfirmModal from "@/components/modals/PurchaseConfirmModal.vue";
import ReadConfirmModal from "@/components/modals/ReadConfirmModal.vue";
import IssueCoverModal from "@/components/modals/IssueCoverModal.vue";
import EditIcon from "@/assets/EditIcon.vue";
import TagLink from "@/components/common/TagLink.vue";
import getSymbolFromCurrency from "currency-symbol-map";
import { hasCustomIssueTitle, issueDisplayLabel, issueNumberLabel } from "@/utils/issueTitle";

const route = useRoute();
const toast = useToast();

// Read on every fetch: the component is reused when moving between issues of the same series.
const routeParams = () => ({
  seriesId: Number(route.params.seriesId as string),
  slug: String(route.params.slug ?? ""),
  number: Number(route.params.number as string),
});

const showPriceModal = ref(false);
const showReadModal = ref(false);
const showCoverModal = ref(false);
const coverSaving = ref(false);
const { preferred_currency } = useUserStore().getUser();
// The store holds a currency code (e.g. "INR"); show its symbol, falling back to the code.
const currencySymbol = getSymbolFromCurrency(preferred_currency) || preferred_currency || "";

const issue = ref<Issue | null>(null);
const neighbours = ref<IssueNeighbours | null>(null);
const themecolor = ref<string | null>(null);
const image = ref<string | null>(null);

const editForm = reactive({
  bought_price: null as number | null,
  bought_date: "",
  read_date: "",
});

const hasCustomTitle = computed(() => !!issue.value && hasCustomIssueTitle(issue.value.title, issue.value.number));
const accentStyle = computed(() => (themecolor.value ? { color: `rgb${themecolor.value}` } : {}));
const accentBorderStyle = computed(() => (themecolor.value ? { borderColor: `rgb${themecolor.value}` } : {}));

const seriesRoute = computed(() =>
  issue.value ? { path: `/series/${issue.value.series.id}-${issue.value.series.slug}` } : { path: "/collection" }
);
const editRoute = computed(() => {
  const { seriesId, slug, number } = routeParams();
  return { name: "EditIssue", params: { seriesId: String(seriesId), slug, number: String(number) } };
});
function issueRoute(number: number) {
  const { seriesId, slug } = routeParams();
  return { name: "IssueDetail", params: { seriesId: String(seriesId), slug, number: String(number) } };
}

async function getIssueDetails() {
  const { seriesId, number } = routeParams();
  try {
    const response = await IssueService.getIssue(seriesId, number);
    issue.value = response.data;

    if (!issue.value) return;

    editForm.bought_price = issue.value.bought_price;
    editForm.bought_date = issue.value.bought_date?.substring(0, 10) || "";
    editForm.read_date = issue.value.read_date?.substring(0, 10) || "";

    const parent = issue.value.series;
    if (parent) {
      themecolor.value = parent.dominant_color;
    }

    // The issue's own cover wins; otherwise fall back to the series cover.
    const seriesImage = parent?.thumbnail
      ? `${SeriesService.getSeriesImageById(parent.id, parent.last_updated)}`
      : null;
    image.value = issue.value.thumbnail
      ? IssueService.getIssueImageById(issue.value.id, issue.value.last_updated)
      : seriesImage;
  } catch (error) {
    console.error("Error fetching issue details:", error);
  }
}

async function getNeighbours() {
  const { seriesId, number } = routeParams();
  try {
    const response = await IssueService.getIssueNeighbours(seriesId, number);
    neighbours.value = response.data;
  } catch (error) {
    neighbours.value = null;
    console.error("Error fetching issue neighbours:", error);
  }
}

function loadIssue() {
  getIssueDetails();
  getNeighbours();
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

function coverErrorMessage(error: any): string {
  return error?.response?.data?.error || error?.message || String(error);
}

async function saveIssueCover(source: File | string) {
  if (!issue.value) return;
  coverSaving.value = true;

  try {
    await IssueService.updateIssueCover(issue.value.id, source);
    showCoverModal.value = false;
    toast.add({ severity: "success", summary: "Cover Updated", detail: "Issue cover updated.", life: 2000 });
    await getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Cover Update Failed", detail: coverErrorMessage(error), life: 4000 });
  } finally {
    coverSaving.value = false;
  }
}

async function removeIssueCover() {
  if (!issue.value) return;
  coverSaving.value = true;

  try {
    await IssueService.removeIssueCover(issue.value.id);
    showCoverModal.value = false;
    toast.add({ severity: "success", summary: "Cover Removed", detail: "Showing the series cover again.", life: 2000 });
    await getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Cover Removal Failed", detail: coverErrorMessage(error), life: 4000 });
  } finally {
    coverSaving.value = false;
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
    getIssueDetails();
  } catch (error) {
    toast.add({ severity: "error", summary: "Update Failed", detail: String(error), life: 3000 });
  }
}

const formatDate = (dateString: string | Date) =>
  new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });

const formatMonth = (dateString: string | Date) =>
  new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'long' });

watch(
  () => [route.params.seriesId, route.params.number],
  () => {
    // Clear the previous issue's cover and neighbours before the new ones load.
    image.value = null;
    neighbours.value = null;
    loadIssue();
  }
);

onMounted(loadIssue);

watch(image, (newImage) => {
  const app = document.querySelector('#app') as HTMLElement;
  if (app) app.style.background = newImage ? `linear-gradient(rgba(18, 25, 43, 0.94), rgba(18, 25, 43, 0.88)), url(${newImage}) center / cover no-repeat fixed` : '';
});

onUnmounted(() => {
  const app = document.querySelector('#app') as HTMLElement;
  if (app) app.style.background = '';
});

async function updateRating(newRating: number) {
  if (!issue.value) return;
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
