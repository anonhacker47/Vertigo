<template>
  <form autocomplete="on" class="z-0 flex items-center justify-evenly flex-1 p-4 gap-6 md:gap-4 md:flex-row flex-col">

    <div class="w-[24rem] h-[38rem]">
      <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
    </div>

    <EditSeriesForm v-model="seriesData" :showIssueSection="showIssueSection" @update-series="updateSeries" />

  </form>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute,useRouter } from "vue-router";

import type { Series } from "@/types/series.types";

import SeriesService from "../services/SeriesService";

import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import EditSeriesForm from "@/components/forms/EditSeriesForm.vue";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);
const router = useRouter();
const route = useRoute();

const seriesId = Number(route.params.Id);


const showIssueSection = ref(false);


async function getSeries() {
  try {
    const response = await SeriesService.getSeriesbyId(seriesId)
    seriesData.value = { ...response };
    console.log(seriesData);    
    imagesrc.value = `${SeriesService.getImagebyId(seriesId)}?t=${Date.now()}`
    } catch (error) {
    console.log(error);
  }
}

async function updateSeries() {
  try {
    const formData = new FormData();

    const data = seriesData.value;

    // Basic fields
    formData.append("title", data.title || "");
    formData.append("description", data.description || "");
    formData.append("series_format", data.series_format || "");
    formData.append("issue_count", String(data.issue_count || 0));
    formData.append("read_count", String(data.read_count || 0));
    formData.append("owned_count", String(data.owned_count || 0));
    formData.append("main_character", data.main_character || "");
    // Convert arrays to JSON strings
    formData.append("genre", JSON.stringify(data.genre || []));
    formData.append("creator", JSON.stringify(data.creator || []));
    formData.append("publisher", (data.publisher && typeof data.publisher === "string")
      ? data.publisher
      : (Array.isArray(data.publisher) ? data.publisher[0] : ""));

    // Handle thumbnail file (only append if it's a File)
    if (seriesData.value.thumbnail) {
      console.log(seriesData.value.thumbnail);

      formData.append("thumbnail", seriesData.value.thumbnail);
    } else {

      console.log("No thumbnail provided.");
    }

    const response = await SeriesService.updateSeries(seriesId, formData);
    router.push({ name: 'SeriesDetail', params: { Id: String(response.data.id), Link: response.data.link } });

  } catch (error) {
    console.error("Update error:", error);
  }
}

const seriesData = ref<Partial<Series>>({
  title: '',
  creator: [],
  description: '',
  genre: [],
  main_character: '',
  series_format: '',
  issue_count: 1,
  thumbnail: '',
  publisher: '',
  read_count: 0,
  owned_count: 0
})

onMounted(() => {
  getSeries();  
});

watch(imagesrc, (val) => {
  console.log("SeriesData changed:", val);
});


function onImageChange(file: File | string) {
  seriesData.value.thumbnail = file;
  if (file instanceof File) {
    imagesrc.value = URL.createObjectURL(file);
  } else if (typeof file === 'string') {
    imagesrc.value = file;
  }
  console.log("Image Changed:", seriesData.value.thumbnail);
}
</script>

<style scoped>
img {
  color: red;
  font-size: x-large;
  text-align: center;
}
</style>
