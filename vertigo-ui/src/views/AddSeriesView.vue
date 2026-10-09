<template>
  <div class="mx-auto w-full max-w-page px-4 pt-6 md:px-8">
    <header>
      <h1 class="text-3xl font-extrabold tracking-tight text-white">Add a series</h1>
      <p class="mt-1 text-sm font-semibold text-slate-400">Import from Metron or MyAnimeList, or fill in the details yourself.</p>
    </header>

    <form
      id="series-form"
      class="mt-7 grid gap-8 md:grid-cols-[14rem_minmax(0,1fr)] md:gap-10 xl:grid-cols-[16rem_minmax(0,1fr)]"
      autocomplete="on"
      novalidate
      @submit.prevent
    >
      <aside class="mx-auto w-56 max-w-full md:sticky md:top-[calc(var(--spacing-header)+1.5rem)] md:mx-0 md:w-auto md:self-start">
        <ImageUploader v-model="imagesrc" v-model:imageLink="imageLinkInput" :title="seriesData.title" @image-change="onImageChange" />
      </aside>

      <div class="min-w-0" :class="{ 'just-imported': justImported }">
        <div class="import-bar">
          <SegmentedControl
            :model-value="importSource"
            :options="sourceOptions"
            label="Source"
            @update:model-value="importSource = $event as ImportSource"
          />
          <SearchMetron v-if="importSource === 'comic'" class="basis-full sm:basis-0" @select="onMetronSelect" />
          <SearchManga v-else class="basis-full sm:basis-0" @select="onMetronSelect" />
        </div>
        <p class="fm-hint mb-7 mt-2.5">Importing fills in the details, cover and issue list. Everything stays editable.</p>

        <SeriesDetailsForm v-model="seriesData" :errors="errors" />

        <IssuesForm
          v-model:readAll="readAll"
          v-model:haveAll="haveAll"
          v-model:issues="issues"
          v-model:issueCount="seriesData.issue_count"
          :imagesrc="imagesrc"
          :manga="seriesData.manga"
        />
      </div>
    </form>
  </div>

  <div class="fm-actionbar">
    <div class="mx-auto flex w-full max-w-page items-center justify-between gap-4 px-4 md:px-8">
      <p class="fm-hint min-w-0 truncate">{{ summaryLine }}</p>
      <div class="flex shrink-0 items-center gap-3">
        <RouterLink to="/collection" class="fm-btn fm-btn--ghost">Cancel</RouterLink>
        <button type="button" class="fm-btn fm-btn--primary" :disabled="creating" @click="createSeries">
          <i v-if="creating" class="pi pi-spin pi-spinner" style="font-size: 13px"></i>
          <span>{{ creating ? "Creating" : "Create series" }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, toRaw, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue";

import type { Series } from "@/types/series.types";
import type { Issue, IssueDraft } from "@/types/issue.types";

import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";

import SegmentedControl from "@/components/common/SegmentedControl.vue";
import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import SeriesDetailsForm, { type SeriesFormErrors } from "@/components/forms/SeriesDetailsForm.vue";
import IssuesForm from "@/components/createSeries/IssuesForm.vue";
import SearchMetron from "@/components/createSeries/SearchMetron.vue";
import SearchManga from "@/components/createSeries/SearchManga.vue";

type ImportSource = "comic" | "manga";

const router = useRouter();
const toast = useToast();

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);
const imageLinkInput = ref("");
const importSource = ref<ImportSource>("comic");
const sourceOptions = [
  { label: "Comics", value: "comic" },
  { label: "Manga", value: "manga" },
];

const readAll = ref(false);
const haveAll = ref(false);
const issues = ref<IssueDraft[]>([]);
const errors = ref<SeriesFormErrors>({});
const creating = ref(false);
const justImported = ref(false);

let isImportingMetronData = false;

const seriesData = ref<Partial<Series>>({
  title: "",
  creator: [],
  description: "",
  notes: "",
  genre: [],
  character: [],
  series_format: "",
  issue_count: 1,
  thumbnail: "",
  publisher: null,
  read_count: 0,
  manga: false,
  owned_count: 0,
  metron_id: null,
  metron_url: null,
});

const summaryLine = computed(() => {
  const title = seriesData.value.title?.trim() || "Untitled series";
  const n = issues.value.length;
  const owned = issues.value.filter((issue) => issue.have).length;
  const read = issues.value.filter((issue) => issue.read).length;
  return `${title}: ${n} ${n === 1 ? "issue" : "issues"}, ${owned} owned, ${read} read`;
});

function updateIssuesCount(newCount: number) {
  const currentLength = issues.value.length;

  if (newCount > currentLength) {
    for (let i = currentLength; i < newCount; i++) {
      issues.value.push({
        title: "",
        read: false,
        have: false,
        purchaseDate: null,
        readDate: null,
        price: null,
        metron_id: null,
        metron_url: null,
        cover: null,
      });
    }
  } else if (newCount < currentLength) {
    issues.value.splice(newCount);
  }
}

// One short highlight on the filled-in form so the import visibly lands.
async function pulseImported() {
  justImported.value = false;
  await nextTick();
  justImported.value = true;
  window.setTimeout(() => { justImported.value = false; }, 1500);
}

function onMetronSelect(seriesDetail: any, seriesEntities: any, metronIssues: any[] = []) {
  isImportingMetronData = true;

  imageLinkInput.value = seriesDetail.image_first_issue || seriesDetail.image_url || "";

  const isManga = importSource.value === "manga";
  const targetCount = (isManga ? Number(seriesDetail.volume_count) : Number(seriesDetail.issue_count)) || 1;

  issues.value = Array.from({ length: targetCount }, (_, index) => {
    const currentNumber = index + 1;
    const matched = metronIssues.find(
      (mi) => Number(mi.number) === currentNumber || String(mi.number) === String(currentNumber)
    );
    return {
      title: "",
      read: false,
      have: false,
      purchaseDate: null,
      readDate: null,
      price: null,
      metron_id: matched ? Number(matched.metron_id) : null,
      metron_url: matched ? matched.metron_url : null,
      // Metron only prefills the cover; whatever is in the field at submit time is what gets sent.
      cover: matched?.image || null,
    };
  });

  seriesData.value = {
    title: seriesDetail.name,
    creator: seriesEntities?.creators || [],
    description: seriesDetail.desc || "",
    notes: seriesData.value.notes || "",
    genre: seriesDetail.genres || [],
    character: seriesEntities?.characters || [],
    series_format: seriesData.value.series_format || "",
    issue_count: targetCount,
    thumbnail: "",
    publisher: seriesDetail.publisher || null,
    read_count: 0,
    manga: isManga,
    owned_count: 0,
    metron_id: isManga ? null : seriesDetail.metron_id || null,
    metron_url: isManga ? null : seriesDetail.metron_url || null,
  };

  haveAll.value = false;
  readAll.value = false;
  errors.value = {};
  pulseImported();

  queueMicrotask(() => {
    isImportingMetronData = false;
  });
}

watch(importSource, (source) => {
  seriesData.value.manga = source === "manga";
});

watch(
  () => seriesData.value.issue_count,
  (newCount) => {
    if (isImportingMetronData) return;

    const sanitizedCount = Number(newCount) || 0;
    if (sanitizedCount !== issues.value.length) {
      updateIssuesCount(sanitizedCount);
    }
  },
  { immediate: true }
);

// Clear a field's error as soon as it is fixed.
watch(() => seriesData.value.title, (title) => {
  if (errors.value.title && title?.trim()) errors.value = { ...errors.value, title: undefined };
});
watch(() => seriesData.value.series_format, (format) => {
  if (errors.value.series_format && format) errors.value = { ...errors.value, series_format: undefined };
});

function validate(): boolean {
  const next: SeriesFormErrors = {};
  if (!seriesData.value.title?.trim()) next.title = "Give the series a title.";
  if (!seriesData.value.series_format) next.series_format = "Choose a format.";
  errors.value = next;

  const firstInvalid = next.title ? "series-title" : next.series_format ? "series-format" : null;
  if (!firstInvalid) return true;

  const el = document.getElementById(firstInvalid);
  el?.scrollIntoView({ block: "center", behavior: "smooth" });
  el?.focus({ preventScroll: true });
  toast.add({ severity: "warn", summary: "Missing details", detail: "Add a title and choose a format.", life: 3000 });
  return false;
}

async function createSeries() {
  if (creating.value || !validate()) return;
  creating.value = true;

  try {
    const owned_count = issues.value.filter((issue) => issue.have).length;
    const read_count = issues.value.filter((issue) => issue.read).length;
    seriesData.value.issue_count = issues.value.length;

    const payload = {
      title: (seriesData.value.title ?? "").trim(),
      publisher: seriesData.value.publisher || [],
      creator: seriesData.value.creator || [],
      description: seriesData.value.description || "",
      notes: seriesData.value.notes || "",
      genre: seriesData.value.genre || [],
      character: seriesData.value.character || [],
      series_format: seriesData.value.series_format || "",
      issue_count: seriesData.value.issue_count || 0,
      read_count: read_count,
      owned_count: owned_count,
      metron_id: seriesData.value.metron_id || null,
      metron_url: seriesData.value.metron_url || null,
      manga: seriesData.value.manga || false,
    };

    const formData = new FormData();
    for (const [key, value] of Object.entries(payload)) {
      if (value === null || value === undefined) {
        formData.append(key, "");
      } else if (typeof value === "object") {
        if (!Array.isArray(value)) {
          formData.append(key, JSON.stringify([value]));
        } else {
          formData.append(key, JSON.stringify(value));
        }
      } else {
        formData.append(key, value.toString());
      }
    }

    if (seriesData.value.thumbnail) {
      formData.append("thumbnail", seriesData.value.thumbnail);
    }

    const rawPublisher = toRaw(seriesData.value.publisher);

    if (!rawPublisher || !rawPublisher.value) {
      formData.delete("publisher");
    } else {
      formData.set("publisher", JSON.stringify([rawPublisher]));
    }

    const response = await SeriesService.addSeries(formData);
    const seriesId = response?.id;

    if (seriesId) {
      await addIssues(seriesId);
      toast.add({
        severity: "success",
        summary: "Series created",
        detail: `${payload.title} is on the shelf.`,
        life: 3000,
      });

      if (seriesData.value.metron_id) {
        toast.add({
          severity: "info",
          summary: "Metron sync started",
          detail: "New creators, characters and publisher details will be synced in the background.",
          life: 5000,
        });
      }

      router.push({
        name: "SeriesDetail",
        params: { Link: response.slug, Id: seriesId },
      });
    } else {
      toast.add({ severity: "error", summary: "Could not create series", detail: "The server did not return a series.", life: 3000 });
    }
  } catch (error: any) {
    console.error("Error creating series:", error);
    toast.add({ severity: "error", summary: "Could not create series", detail: error.message || "Unexpected error.", life: 3000 });
  } finally {
    creating.value = false;
  }
}

async function addIssues(seriesId: number) {
  try {
    if (!issues.value.length) return;

    const issuePayload = issues.value.map((issue, index) => ({
      number: index + 1,
      title: issue.title?.trim() || String(index + 1),
      is_owned: issue.have,
      is_read: issue.read,
      bought_date: issue.purchaseDate ? new Date(issue.purchaseDate).toISOString() : null,
      read_date: issue.readDate ? new Date(issue.readDate).toISOString() : null,
      bought_price: issue.price || null,
      metron_id: issue.metron_id || null,
      metron_url: issue.metron_url || null,
    }));

    const response = await IssueService.addIssues(seriesId, issuePayload);
    await uploadIssueCovers(response.data);
  } catch (error: any) {
    console.error("Error adding issues:", error.response?.data || error);
  }
}

/**
 * Upload the per-issue covers picked in the form, matched to the created issues by number.
 * File covers are saved inline and awaited; URL covers are queued server-side (background=true)
 * and do not hold up navigation. One warning toast is shown if any upload fails.
 */
function uploadIssueCovers(createdIssues: Pick<Issue, "id" | "number">[]): Promise<void> {
  const created = Array.isArray(createdIssues) ? createdIssues : [];
  const inline: Promise<unknown>[] = [];
  const background: Promise<unknown>[] = [];

  issues.value.forEach((issue, index) => {
    const cover = issue.cover instanceof File ? issue.cover : (issue.cover?.trim() || null);
    if (!cover) return;

    const number = index + 1;
    const match = created.find((c) => Number(c.number) === number);
    if (!match?.id) {
      inline.push(Promise.reject(new Error(`Issue #${number} was not returned by the server; cover skipped.`)));
      return;
    }

    if (cover instanceof File) {
      inline.push(IssueService.updateIssueCover(match.id, cover));
    } else {
      background.push(IssueService.updateIssueCover(match.id, cover, { background: true }));
    }
  });

  const all = [...inline, ...background];
  if (!all.length) return Promise.resolve();

  // Report once everything has settled; for background uploads this may be after navigation.
  Promise.allSettled(all).then((results) => {
    const failed = results.filter((r): r is PromiseRejectedResult => r.status === "rejected");
    if (!failed.length) return;

    failed.forEach((r) => console.error("Issue cover upload failed:", r.reason?.response?.data || r.reason));
    toast.add({
      severity: "warn",
      summary: "Some covers not uploaded",
      detail: `${failed.length} of ${all.length} issue cover(s) could not be uploaded; the series cover will be shown for those.`,
      life: 6000,
    });
  });

  return Promise.allSettled(inline).then(() => undefined);
}

function onImageChange(file: File | string) {
  seriesData.value.thumbnail = file;
  if (file instanceof File) {
    imagesrc.value = URL.createObjectURL(file);
  } else if (typeof file === "string") {
    imagesrc.value = file;
  }
}
</script>

<style scoped>
/* The import bar: one wide field with the source switch inside it. */
.import-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(11, 18, 32, 0.6);
  transition: border-color 0.12s ease, box-shadow 0.12s ease;
}
.import-bar:focus-within {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.18);
}

/* A single wash over the form when an import lands, then gone. */
.just-imported {
  border-radius: 12px;
  animation: import-pulse 1.5s ease-out;
}
@keyframes import-pulse {
  from { background-color: rgba(56, 189, 248, 0.1); }
  to { background-color: transparent; }
}

@media (prefers-reduced-motion: reduce) {
  .import-bar { transition: none; }
  .just-imported { animation: none; }
}
</style>
