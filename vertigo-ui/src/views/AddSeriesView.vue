<template>
  <div class="w-full flex flex-col items-center justify-center m-4 mb-2">
    <h1 class="text-3xl font-bold">Create Series</h1>
  </div>

  <form autocomplete="on" class="z-0 flex items-center justify-center flex-1 gap-6 md:gap-12 md:flex-row flex-col">

    <div class="w-[24rem] h-[38rem]">
      <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
    </div>

    <SeriesForm v-model="seriesData" :showIssueSection="showIssueSection" @next="showIssueSection = true" />

    <IssuesForm v-model:readAll="readAll" v-model:haveAll="haveAll" :showIssueSection="showIssueSection"
      :seriesData="seriesData" :issues="issues" :imagesrc="imagesrc" @cancel="showIssueSection = false"
      @submit="createSeries" />

  </form>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

import type { Series } from "@/types/series.types";

import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";

import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import SeriesForm from "@/components/createSeries/CreateSeriesForm.vue";
import IssuesForm from "@/components/createSeries/IssuesForm.vue";
import { useToast } from "primevue";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const imageLinkInput = ref("");

const router = useRouter();
const toast = useToast();

const showIssueSection = ref(false);
const readAll = ref(false);
const haveAll = ref(false);
const issues = ref([]);

const seriesData = ref<Partial<Series>>({
  title: '',
  creator: [],
  description: '',
  genre: [],
  character: [],
  series_format: '',
  issue_count: 1,
  thumbnail: '',
  publisher: '',
  read_count: 0,
  owned_count: 0
})

function toggleAll(type: string) {
  issues.value.forEach((issue) => {
    issue[type] = type === "read" ? readAll.value : haveAll.value;
  });
}

watch(
  () => seriesData.value.issue_count,
  (newCount) => {
    // Adjust the array length to match the new issue count
    haveAll.value = false;
    readAll.value = false;

    issues.value = Array.from({ length: newCount }, () => ({
      read: false,
      have: false,
      purchaseDate: null,
      readDate: null,
      price: null
    }));
  },
  { immediate: true }
);

watch(
  issues,
  (newIssues) => {
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
  if (!seriesData.value.title.trim()) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Title is required.', life: 3000 });
    return;
  }

  try {
    const owned_count = issues.value.filter((issue) => issue.have).length;
    const read_count = issues.value.filter((issue) => issue.read).length;
    seriesData.value.issue_count = issues.value.length;

    const payload = {
      title: seriesData.value.title,
      publisher: seriesData.value.publisher || "",
      creator: seriesData.value.creator || [],
      description: seriesData.value.description || "",
      genre: seriesData.value.genre || [],
      character: seriesData.value.character || "",
      series_format: seriesData.value.series_format || "",
      issue_count: seriesData.value.issue_count || 0,
      read_count: read_count,
      owned_count: owned_count,
    };

    const formData = new FormData();
    for (const key in payload) {
      if (Array.isArray(payload[key])) {
        formData.append(key, JSON.stringify(payload[key]));
      } else {
        formData.append(key, payload[key]?.toString() || "");
      }
    }

    if (seriesData.value.thumbnail) {
      formData.append("thumbnail", seriesData.value.thumbnail);
    }

    const response = await SeriesService.addSeries(formData);
    const seriesId = response?.id;

    if (seriesId) {
      await addIssues(seriesId);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Series created successfully!', life: 3000 });
      router.push({ name: "SeriesDetail", params: { Link: response.slug, Id: seriesId } });
    } else {
      toast.add({ severity: 'error', summary: 'Failure', detail: 'Series creation failed.', life: 3000 });
    }
  } catch (error) {
    console.error("Error creating series:", error);
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Unexpected error.', life: 3000 });
  }
}


async function addIssues(seriesId) {
  try {
    if (!issues.value.length) {
      console.log("No issues to add.");
      return;
    }

    // Construct the payload with all issues at once
    // Construct the payload as a direct list (not an object with "issues" key)
    const issuePayload = issues.value.map((issue, index) => ({
      number: index + 1,
      title: String(index + 1), // Title as string
      is_owned: issue.have, // Ensure this matches the backend
      is_read: issue.read,
      bought_date: issue.purchaseDate ? new Date(issue.purchaseDate).toISOString() : null,
      read_date: issue.readDate ? new Date(issue.readDate).toISOString() : null,
      bought_price: issue.price || null,
    }));

    // Send all issues in a single API call
    await IssueService.addIssues(seriesId, issuePayload);
    console.log("Issues added successfully!");
  } catch (error) {
    console.error("Error adding issues:", error.response?.data || error);
  }
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
