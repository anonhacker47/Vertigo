<template>
  <div class="w-full flex flex-col items-center justify-center my-4 mb-2">
    <h1 class="text-3xl font-bold">Create Series</h1>
  </div>

  <form @submit.prevent autocomplete="on"
    class="z-0 flex items-start justify-center flex-1 gap-6 md:gap-12 md:flex-row flex-col">

    <div class="w-94 h-152">
      <ImageUploader v-model="imagesrc" v-model:imageLink="imageLinkInput" @image-change="onImageChange" />
    </div>

    <div class="w-[90%] md:w-2/4 flex flex-col items-start justify-start">

      <div class="flex gap-8 mb-4">
        <div class="w-full max-w-xs rounded-2xl border border-base-300 bg-base-100 p-4 shadow-sm">
          <div class="mb-4 w-full max-w-xs">
            <label class="mb-1 block text-sm font-medium text-base-content">
              Series Type
            </label>
            <Select v-model="importSource" :options="seriesTypeOptions" optionLabel="label" optionValue="value"
              placeholder="Select series type" class="w-full" />
          </div>
        </div>

        <SearchMetron v-if="importSource === 'comic'" @select="onMetronSelect" />

        <SearchManga v-else @select="onMetronSelect" />
      </div>
      <SeriesForm v-model="seriesData" :showIssueSection="showIssueSection" @next="showIssueSection = true" />
      <IssuesForm v-model:readAll="readAll" v-model:haveAll="haveAll" v-model:issues="issues"
        :showIssueSection="showIssueSection" :seriesData="seriesData" :imagesrc="imagesrc"
        @cancel="showIssueSection = false" @submit="createSeries" />
    </div>

  </form>
</template>

<script setup lang="ts">
import { ref, toRaw, watch } from "vue";
import { useRouter } from "vue-router";

import type { Series } from "@/types/series.types";
import type { Issue, IssueDraft } from "@/types/issue.types";

import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";

import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import SeriesForm from "@/components/createSeries/CreateSeriesForm.vue";
import IssuesForm from "@/components/createSeries/IssuesForm.vue";
import { useToast } from "primevue";
import SearchMetron from "@/components/createSeries/SearchMetron.vue";
import SearchManga from "@/components/createSeries/SearchManga.vue";
import Select from "primevue/dropdown";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);
const importSource = ref<'comic' | 'manga'>('comic');

const seriesTypeOptions = [
  { label: 'Comics', value: 'comic' },
  { label: 'Manga', value: 'manga' },
];

const imageLinkInput = ref("");
const router = useRouter();
const toast = useToast();

const showIssueSection = ref(false);
const readAll = ref(false);
const haveAll = ref(false);
const issues = ref<IssueDraft[]>([]);

let isImportingMetronData = false;

const seriesData = ref<Partial<Series>>({
  title: '',
  creator: [],
  description: '',
  genre: [],
  character: [],
  series_format: '',
  issue_count: 1,
  thumbnail: '',
  publisher: {
    id: null,
    name: null
  },
  read_count: 0,
  manga: false,
  owned_count: 0,
  metron_id: null,
  metron_url: null,
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
        cover: null
      });
    }
  } else if (newCount < currentLength) {
    issues.value.splice(newCount);
  }
}

function onMetronSelect(seriesDetail, seriesEntities, metronIssues = []) {
  isImportingMetronData = true;

  imageLinkInput.value = seriesDetail.image_first_issue || seriesDetail.image_url || '';
  
  const targetCount = Number(seriesDetail.issue_count) || 1;

  issues.value = Array.from({ length: targetCount }, (_, index) => {
    const currentNumber = index + 1;
    const matched = metronIssues.find(
      mi => Number(mi.number) === currentNumber || String(mi.number) === String(currentNumber)
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
      cover: matched?.image || null
    };
  });

  seriesData.value = {
    title: seriesDetail.name,
    creator: seriesEntities?.creators || [],
    description: seriesDetail.desc || '',
    genre: seriesDetail.genres || [],
    character: seriesEntities?.characters || [],
    series_format: '',
    issue_count: targetCount, 
    thumbnail: '',
    publisher: seriesDetail.publisher || { id: null, name: '' },
    read_count: 0,
    manga: importSource.value === 'manga',
    owned_count: 0,
    metron_id: seriesDetail.metron_id || null,
    metron_url: seriesDetail.metron_url || null
  };
  
  haveAll.value = false;
  readAll.value = false;

  queueMicrotask(() => {
    isImportingMetronData = false;
  });
}

watch(importSource, (source) => {
  seriesData.value.manga = source === 'manga';
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

watch(
  issues,
  (newIssues) => {
    if (!newIssues) return;
    newIssues.forEach((issue) => {
      const today = new Date().toISOString().split('T')[0];

      if (issue.have && !issue.purchaseDate) {
        issue.purchaseDate = today;
      }
      if (issue.read && !issue.readDate) {
        issue.readDate = today;
      }
    });
  },
  { deep: true }
);

async function createSeries() {
  if (!seriesData.value.title?.trim()) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Title is required.', life: 3000 });
    return;
  }

  try {
    const owned_count = issues.value.filter((issue) => issue.have).length;
    const read_count = issues.value.filter((issue) => issue.read).length;
    seriesData.value.issue_count = issues.value.length;

    const payload = {
      title: seriesData.value.title,
      publisher: seriesData.value.publisher || [],
      creator: seriesData.value.creator || [],
      description: seriesData.value.description || "",
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
    for (const key in payload) {
      const value = payload[key];

      if (value === null || value === undefined) {
        formData.append(key, "");
      }
      else if (typeof value === "object") {
        if (!Array.isArray(value)) {
          formData.append(key, JSON.stringify([value]));
        } else {
          formData.append(key, JSON.stringify(value));
        }
      }
      else {
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
        severity: 'success',
        summary: 'Series Created',
        detail: 'Series created successfully.',
        life: 3000
      });

      if (seriesData.value.metron_id) {
        toast.add({
          severity: 'info',
          summary: 'Metron Sync Started',
          detail: 'New creators, characters, and publisher metadata will be synced in the background.',
          life: 5000
        });
      }

      router.push({
        name: "SeriesDetail",
        params: { Link: response.slug, Id: seriesId }
      });

    } else {
      toast.add({ severity: 'error', summary: 'Failure', detail: 'Series creation failed.', life: 3000 });
    }
  } catch (error: any) {
    console.error("Error creating series:", error);
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Unexpected error.', life: 3000 });
  }
}

async function addIssues(seriesId: number) {
  try {
    if (!issues.value.length) {
      console.log("No issues to add.");
      return;
    }

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
    console.log("Issues added successfully!");

    await uploadIssueCovers(response.data);
  } catch (error) {
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
  } else if (typeof file === 'string') {
    imagesrc.value = file;
  }
}
</script>

<style scoped>
img {
  color: red;
  font-size: x-large;
  text-align: center;
}
</style>
