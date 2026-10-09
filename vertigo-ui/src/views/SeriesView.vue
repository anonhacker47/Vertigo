<template>
  <div v-if="series" :key="series.id" class="select-none">
    <div class="flex w-full flex-col md:h-[calc(100vh-var(--spacing-header))]">

      <nav class="hidden grid-cols-2 items-center gap-4 border-b border-slate-600 px-6 py-3 text-sm md:grid">
        <RouterLink v-if="neighbours.previous" :to="seriesRoute(neighbours.previous)" title="Previous series"
          class="justify-self-start flex min-w-0 max-w-full items-center gap-2 rounded-md px-3 py-1.5 text-slate-300 transition hover:bg-slate-800 hover:text-white">
          <i class="pi pi-chevron-left text-xs" :style="accentStyle"></i>
          <span class="truncate font-semibold" :style="accentStyle">{{ neighbours.previous.title || 'series' }}</span>
        </RouterLink>
        <span v-else></span>

        <RouterLink v-if="neighbours.next" :to="seriesRoute(neighbours.next)" title="Next series"
          class="justify-self-end flex min-w-0 max-w-full items-center gap-2 rounded-md px-3 py-1.5 text-slate-300 transition hover:bg-slate-800 hover:text-white">
          <span class="truncate font-semibold" :style="accentStyle">{{ neighbours.next.title || 'series' }}</span>
          <i class="pi pi-chevron-right text-xs" :style="accentStyle"></i>
        </RouterLink>
        <span v-else></span>
      </nav>

      <div class="flex flex-1 flex-col md:flex-row md:overflow-hidden">

        <section class="flex w-full flex-col gap-5 px-6 py-6 md:w-1/2 md:basis-1/2 md:overflow-y-auto md:px-8 md:pb-10">

          <div class="flex flex-col gap-6 xl:flex-row xl:gap-7">
            <div class="mx-auto flex w-44 shrink-0 flex-col gap-2.5 xl:mx-0">
              <img v-if="image && image !== 'noimage'" :src="image" :alt="`${series.title} cover`"
                class="w-full rounded-lg border-2 border-primary object-cover" :style="accentBorderStyle" />
              <div v-else
                class="flex aspect-[2/3] w-full items-center justify-center rounded-lg border-2 border-primary bg-slate-900 p-4 text-center"
                :style="accentBorderStyle">
                <span class="break-words text-2xl font-semibold opacity-70" :style="accentStyle">
                  {{ series.title }}
                </span>
              </div>

              <a v-if="series.metron_url" :href="series.metron_url" target="_blank" rel="noopener noreferrer"
                class="flex items-center justify-center gap-2 rounded-sm border border-slate-600 bg-slate-900 px-2 py-1 text-sm font-semibold text-slate-300 transition hover:bg-slate-700"
                :style="accentStyle">
                View on Metron
                <i class="pi pi-external-link text-sm"></i>
              </a>
              <p v-if="series.metron_id" class="select-all text-center text-sm text-slate-400" :style="accentStyle">
                Metron ID: {{ series.metron_id }}
              </p>
            </div>

            <div class="flex min-w-0 flex-1 flex-col gap-4">
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <h1 class="break-words text-3xl font-extrabold leading-[1.15] tracking-tight text-primary xl:text-4xl"
                    :style="accentStyle">
                    {{ series.title }}
                  </h1>
                  <div class="mt-3 flex flex-wrap items-center gap-2 text-sm">
                    <TagLink v-if="series.publisher" :label="series.publisher.title"
                      :to="`/publisher/${series.publisher.id}-${series.publisher.slug}`" :color="tagColor" />
                    <TagLink v-if="series.series_format" :label="series.series_format"
                      :to="{ path: '/collection', query: { series_format: series.series_format } }" :color="tagColor" />
                    <span v-if="startedYear" class="text-slate-400">Started {{ startedYear }}</span>
                  </div>
                </div>

                <div class="tooltip tooltip-success tooltip-left shrink-0" data-tip="Edit Series">
                  <RouterLink :to="{ name: 'EditSeries', params: { Link: series.slug, Id: series.id } }"
                    class="flex h-10 w-10 items-center justify-center rounded-full transition duration-200 ease-in-out hover:scale-110 hover:border-2 hover:border-emerald-400">
                    <EditIcon class="h-6 w-6" :fill-color="iconColor" />
                  </RouterLink>
                </div>
              </div>
 
              <Rating @update:model-value="updateRating" :modelValue="series.user_rating" :cancel="false" :stars="5" :style="ratingStyle" />

              <div v-if="issuesList.length" class="mt-1 flex flex-col gap-3.5">
                <div v-for="track in progressTracks" :key="track.field" class="flex flex-col gap-1.5">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <div class="flex items-center gap-2 font-semibold text-slate-200">
                      <img :src="track.icon" alt="" width="20" height="20" />
                      <span>{{ track.label }}</span>
                    </div>
                    <span class="tabular-nums text-slate-400">{{ track.count }} of {{ totalIssues }}</span>
                  </div>

                  <div v-if="segmented" class="grid" :class="issuesList.length > 48 ? 'gap-0' : 'gap-0.5'"
                    :style="{ gridTemplateColumns: `repeat(${issuesList.length}, minmax(0, 1fr))` }">
                    <RouterLink v-for="issue in issuesList" :key="issue.id" :to="issueRoute(issue)"
                      :title="segmentTitle(issue, track)" :aria-label="segmentTitle(issue, track)"
                      class="block h-3 rounded-[2px] transition-opacity hover:opacity-70"
                      :class="issue[track.field] ? '' : 'bg-slate-700/70'"
                      :style="issue[track.field] ? { backgroundColor: fillColor } : {}" />
                  </div>
                  <div v-else class="h-3 overflow-hidden rounded-[2px] bg-slate-700/70" role="img"
                    :aria-label="`${track.count} of ${totalIssues} ${track.label.toLowerCase()}`">
                    <div class="h-full"
                      :style="{ width: `${Math.round((track.count / totalIssues) * 100)}%`, backgroundColor: fillColor }">
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-slate-400">No issues yet.</p>
            </div>
          </div>


          <dl v-if="hasTags" class="grid grid-cols-[6rem_minmax(0,1fr)] gap-x-4 gap-y-3 border-t border-slate-800/60 pt-5">
            <template v-if="series.genre?.length">
              <dt class="pt-1 text-sm text-slate-400">Genre</dt>
              <dd class="flex flex-wrap gap-2">
                <TagLink v-for="genre in series.genre" :key="genre" :label="genre"
                  :to="{ path: '/collection', query: { genre } }" :color="tagColor" />
              </dd>
            </template>
            <template v-if="series.character?.length">
              <dt class="pt-1 text-sm text-slate-400">Characters</dt>
              <dd class="flex flex-wrap gap-2">
                <TagLink v-for="character in series.character" :key="character.id || character.title"
                  :label="character.title" :to="`/character/${character.id}-${character.slug}`" :color="tagColor" />
              </dd>
            </template>
            <template v-if="series.creator?.length">
              <dt class="pt-1 text-sm text-slate-400">Creators</dt>
              <dd class="flex flex-wrap gap-2">
                <TagLink v-for="creator in series.creator" :key="creator.id || creator.title"
                  :label="creator.title" :to="`/creator/${creator.id}-${creator.slug}`" :color="tagColor" />
              </dd>
            </template>
          </dl>

          <section class="textbox" :style="proseStyle">
            <div class="mb-2 flex items-baseline justify-between gap-4">
              <h2 class="text-[13px] font-bold text-slate-400">Description</h2>
              <button v-if="descriptionIsLong" type="button" class="text-[13px] font-bold text-sky-400 hover:text-sky-300"
                :aria-expanded="descriptionOpen" @click="descriptionOpen = !descriptionOpen">
                {{ descriptionOpen ? "Show less" : "Read more" }}
              </button>
            </div>
            <p v-if="series.description" class="textbox__text max-w-prose whitespace-pre-line text-[15px] leading-relaxed md:text-base"
              :class="{ 'line-clamp-6': descriptionIsLong && !descriptionOpen }" style="text-wrap: pretty" :style="accentStyle">
              {{ series.description }}
            </p>
            <p v-else class="text-sm text-slate-400">No description yet.</p>
          </section>

          <section class="textbox" :style="proseStyle">
            <h2 class="mb-2 text-[13px] font-bold text-slate-400">Notes</h2>
            <p v-if="series.notes" class="textbox__text max-w-prose whitespace-pre-line text-[15px] leading-relaxed md:text-base" style="text-wrap: pretty">
              {{ series.notes }}
            </p>
            <p v-else class="text-sm text-slate-400" :style="accentStyle">No notes yet.</p>
          </section>
        </section>

        <section class="relative flex w-full flex-col border-slate-700 md:w-1/2 md:basis-1/2 md:border-l">
          <div class="flex flex-wrap items-center justify-between gap-3 px-6 pb-3 pt-5 md:px-8">
            <div>
              <h2 class="text-2xl font-extrabold text-white" :style="accentStyle">Issues</h2>
              <p class="mt-0.5 text-[13px] font-semibold text-slate-400">{{ issuesSummary }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" class="fm-iconbtn fm-iconbtn--danger" :aria-pressed="editMode"
                :title="editMode ? 'Leave delete mode' : 'Delete issues'" aria-label="Delete mode" @click="toggleEditMode">
                <i class="pi pi-trash" style="font-size: 14px"></i>
              </button>
              <Button label="Add issue" icon="pi pi-plus" size="small" @click="showAddIssue = true" />                
            </div>
          </div>

          <div class="w-full flex-1 pb-12 md:overflow-y-auto">
            <div v-if="issuesList.length"
              class="grid grid-cols-1 gap-5 px-6 pt-2 sm:grid-cols-[repeat(auto-fill,minmax(150px,1fr))] sm:gap-x-4 sm:gap-y-6 md:px-8">
              <IssueCard v-for="issue in issuesList" :key="issue.id" :issue="issue" :edit_mode="editMode"
                :preferred_currency="preferred_currency" :image="image" :themecolor="themecolor" :series="series"
                @updateStatus="updateStatus(issue, $event)" @deleteIssue="confirmDelete(issue)" />
            </div>
            <p v-else class="px-6 py-6 text-sm text-slate-400 md:px-8">No issues yet. Use Add issue to start the run.</p>

            <AddIssueModal v-model:visible="showAddIssue" :series-id="series.id" :taken-numbers="takenNumbers"
              :default-number="nextNumber" @added="onIssueAdded" />
          </div>
        </section>
      </div>
    </div>

    <nav v-if="neighbours.previous || neighbours.next" class="flex justify-between gap-3 px-6 pb-8 md:hidden">
      <RouterLink v-if="neighbours.previous" :to="seriesRoute(neighbours.previous)"
        class="flex min-w-0 items-center gap-2 rounded-md bg-slate-800 px-4 py-2 font-bold text-slate-300 transition hover:bg-slate-700"
        :style="accentStyle">
        <i class="pi pi-chevron-left"></i>
        <span class="truncate">{{ neighbours.previous.title || 'Previous series' }}</span>
      </RouterLink>
      <div v-else></div>

      <RouterLink v-if="neighbours.next" :to="seriesRoute(neighbours.next)"
        class="flex min-w-0 items-center gap-2 rounded-md bg-slate-800 px-4 py-2 font-bold text-slate-300 transition hover:bg-slate-700"
        :style="accentStyle">
        <span class="truncate">{{ neighbours.next.title || 'Next series' }}</span>
        <i class="pi pi-chevron-right"></i>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "../store/user";

import type { Series, SeriesNeighbour, SeriesNeighbours } from "@/types/series.types";
import type { Issue } from "@/types/issue.types";

import IssueCard from "../components/cards/IssueCard.vue";
import AddIssueModal from "@/components/modals/AddIssueModal.vue";
import SeriesService from "../services/SeriesService";
import IssueService from "../services/IssueService";
import EditIcon from "@/assets/EditIcon.vue";
import Rating from "primevue/rating";
import { useToast } from "primevue/usetoast";
import { useConfirmAction } from "@/composables/useConfirmAction";
import TagLink from "@/components/common/TagLink.vue";
import { issueDisplayLabel } from "@/utils/issueTitle";
import Button from "primevue/button";

const { confirmAction } = useConfirmAction();
const toast = useToast();

const message = ref();
const neighbours = ref<SeriesNeighbours>({ next: null, previous: null });

function onIssueAdded(issue: Issue) {
  getIssues();
  getIssueCount();
  toast.add({ severity: "success", summary: "Issue added", detail: `#${issue.number} is on the shelf.`, life: 3000 });
}

async function deleteIssue(issueToDelete: Issue) {
  try {
    await IssueService.removeIssue(issueToDelete.id);
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
  const name = issue.title && issue.title !== String(issue.number) ? ` (${issue.title})` : "";
  confirmAction({
    message: `Delete issue #${issue.number}${name}? This cannot be undone.`,
    header: "Delete issue",
    acceptLabel: "Delete",
    severity: "danger",
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
const showAddIssue = ref(false);
const takenNumbers = computed(() => issuesList.value.map((issue) => issue.number));
const nextNumber = computed(() => (takenNumbers.value.length ? Math.max(...takenNumbers.value) + 1 : 1));
const issuesSummary = computed(() => {
  const total = issuesList.value.length;
  if (!total) return "Nothing added yet";
  const owned = issuesList.value.filter((issue) => issue.is_owned).length;
  const read = issuesList.value.filter((issue) => issue.is_read).length;
  return `${total} ${total === 1 ? "issue" : "issues"}, ${owned} owned, ${read} read`;
});

const issueCount = ref({
  owned_count: 0,
  read_count: 0,
  total_count: 0,
});
const themecolor = ref<string | null>(null);
const image = ref<string | null>(null);

const accentStyle = computed(() => (themecolor.value ? { color: `rgb${themecolor.value}` } : {}));
const ratingStyle = computed(() =>
  themecolor.value
    ? { "--p-rating-icon-active-color": `rgb${themecolor.value}`, "--p-rating-icon-hover-color": `rgb${themecolor.value}` }
    : {}
);
// Body text in the boxes carries a light tint of the series colour, kept readable by mixing into slate.
const proseStyle = computed(() => {
  if (!themecolor.value) return {};
  const channels = String(themecolor.value).replace(/[()]/g, "");
  return { "--prose-tint": `color-mix(in srgb, rgb(${channels}) 28%, #e2e8f0)` };
});

const descriptionOpen = ref(false);
const descriptionIsLong = computed(() => {
  const text = series.value?.description ?? "";
  return text.length > 600 || text.split("\n").length > 6;
});
const accentBorderStyle = computed(() => (themecolor.value ? { borderColor: `rgb${themecolor.value}` } : {}));
const tagColor = computed(() => themecolor.value || "(255,255,255)");
const iconColor = computed(() => (themecolor.value ? `rgb${themecolor.value}` : "rgb(203, 213, 225)"));

const startedYear = computed(() => {
  if (!series.value?.release_date) return null;
  const date = new Date(series.value.release_date);
  return Number.isNaN(date.getTime()) ? null : date.getFullYear();
});
const hasTags = computed(() =>
  !!(series.value?.genre?.length || series.value?.character?.length || series.value?.creator?.length)
);

type StatusField = "is_owned" | "is_read";
interface ProgressTrack {
  field: StatusField;
  label: string;
  icon: string;
  count: number;
}
const collectionIcon = new URL("../assets/collection.svg", import.meta.url).href;
const readIcon = new URL("../assets/read.svg", import.meta.url).href;
const progressTracks = computed<ProgressTrack[]>(() => [
  { field: "is_owned", label: "Owned", icon: collectionIcon, count: issueCount.value.owned_count },
  { field: "is_read", label: "Read", icon: readIcon, count: issueCount.value.read_count },
]);
const totalIssues = computed(() => issueCount.value.total_count || issuesList.value.length);
// Past ~120 issues the segments get too thin to hit, so fall back to a plain bar.
const segmented = computed(() => issuesList.value.length <= 120);
const fillColor = computed(() => (themecolor.value ? `rgb${themecolor.value}` : "rgb(74, 222, 128)"));

const issueRoute = (issue: Issue) => ({
  name: "IssueDetail",
  params: { seriesId: String(series.value?.id), slug: series.value?.slug ?? "", number: String(issue.number) },
});
const segmentTitle = (issue: Issue, track: ProgressTrack) =>
  `${issueDisplayLabel(issue.title, issue.number)}: ${issue[track.field] ? "" : "not "}${track.label.toLowerCase()}`;

const seriesRoute = (neighbour: SeriesNeighbour) => `/series/${neighbour.id}-${neighbour.slug}`;

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
      image.value = `${SeriesService.getSeriesImageById(series.value.id, series.value.last_updated)}`;
    }
  } catch (error) {
    console.log(error);
  }
}

async function getIssues() {
  try {
    const result: any = await IssueService.fetchIssues(
      Number(route.params.Id),
      "number",
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

    await IssueService.updateIssue(issue.id, updateData);
    getIssueCount();
  } catch (error) {
    console.log(error);
  }
}

async function updateRating(newRating: number) {
  try {
    const formData = new FormData();
    formData.append("user_rating", String(newRating));

    await SeriesService.updateSeries(Number(route.params.Id), formData);
    await getSeries(Number(route.params.Id));
  } catch (error) {
    console.error("Failed to update rating:", error);
  }
}

async function getNeighbours(id: number) {
  try {
    const res = await SeriesService.getSeriesNeighbours(id);
    neighbours.value = res.data;
  } catch (error) {
    neighbours.value = { next: null, previous: null };
    console.log(error);
  }
}

watch(
  () => route.params.Id,
  (newId) => {
    // Clear the previous series before the new one loads.
    image.value = null;
    series.value = null;
    themecolor.value = null;
    neighbours.value = { next: null, previous: null };
    editMode.value = false;
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

<style scoped>
.textbox {
  padding: 14px 16px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0b1220;
}
.textbox__text {
  color: var(--prose-tint, #e2e8f0);
}
</style>
