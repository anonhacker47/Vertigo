<template>
  <form autocomplete="on" class="z-0 flex items-center justify-evenly flex-1 p-4 gap-6 md:gap-4 md:flex-row flex-col">

    <ImageUploader v-model="imagesrc" @image-change="onImageChange" />

    <SeriesForm v-model="seriesData" :showIssueSection="showIssueSection" @next="showIssueSection = true" />

    <!-- 
      <div v-if="!showIssueSection" class="md:w-2/3  shadow-2xl bg-base-100 h-full w-full card justify-between p-8 flex gap-6 md:gap-10">
        <div class="flex flex-col w-full md:flex-row gap-8 md:gap-20 justify-around">
          <div class="form-control w-full">
            <input type="text" placeholder="Series Name" v-model="seriesData.value.title" class="input w-full input-bordered"
              required />
          </div>
          <div class="form-control w-full">
            <select class="select  w-full select-primary" v-model="seriesData.value.series_format" required>
              <option disabled value="">Pick Format</option>
              <option>Trade Paperback</option>
              <option>Hard Cover</option>
              <option>Omnibus</option>
              <option>Absolute Edition</option>
              <option>Manga</option>
            </select>
          </div>
          <div class="form-control w-full">
            <SingleSelectCombobox v-model="seriesData.value.publisher" field="publisher" placeholder="Publisher" />
          </div>
        </div>

        <div class="flex flex-col md:flex-row gap-8 md:gap-20 justify-around">
          <div class="form-control w-full">
            <MultiSelectCombobox v-model="seriesData.value.genre" field="genre" placeholder="Genre" />
          </div>
          <div class="form-control w-full">
            <SingleSelectCombobox v-model="seriesData.value.main_char" field="main_char" placeholder="Main Character/ Team" />
          </div>
          <div class="form-control w-full">
            <MultiSelectCombobox v-model="seriesData.value.creator" field="creator" placeholder="Creators" />
          </div>
        </div>

        <div class="flex flex-col md:flex-row gap-20 justify-around">
          <div class="form-control w-full">
            <textarea class="textarea textarea-bordered" placeholder="Summary"
              v-model="seriesData.value.description"></textarea>
          </div>
        </div>

        <div class="flex flex-col md:flex-row gap-16 justify-around">
          <div class="form-control w-full">
            <button type="button" @click="router.push('collection')" class="btn btn-danger">
              Cancel
            </button>
          </div>
          <div class="form-control w-full">
            <button @click.prevent="showIssueSection = true" :disabled="!seriesData.value.title"
              class="btn btn-primary rounded">
              Next
            </button>
          </div>
        </div>
      </div> -->


    <!-- <div v-if="showIssueSection"
      class="card h-full  w-full md:w-2/3 flex gap-6 md:gap-8 shadow-2xl bg-base-100 justify-between p-8 ">
      <div class="form-control">
        <label class="label">Number of Issues</label>
        <input type="number" v-model.number="seriesData.issue_count" min="1" class="input input-bordered" />
      </div>

      <div class="flex flex-col md:flex-row gap-4 md:gap-16 justify-around">
        <div class="form-control w-full">
          <div class="form-control">
            <label class="label cursor-pointer flex items-center gap-2"
              :class="haveAll ? 'text-primary' : 'text-white'">
              <span>Have All?</span>
              <input type="checkbox" v-model="haveAll" @change="toggleAll('have')" class="checkbox"
                :class="haveAll ? 'checkbox-primary' : ''" />
            </label>
          </div>
        </div>
        <div class="form-control w-full">
          <div class="form-control">
            <label class="label cursor-pointer flex items-center gap-2" :class="readAll ? 'text-accent' : 'text-white'">
              <span>Read Already?</span>
              <input type="checkbox" v-model="readAll" @change="toggleAll('read')" class="checkbox"
                :class="readAll ? 'checkbox-accent' : ''" />
            </label>
          </div>
        </div>
      </div>

      <div class="grid place-items-center  w-full md:gap-6 md:max-h-[28rem] overflow-y-auto overflow-x-hidden"
        style="grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 1rem;">

        <div v-for="n in seriesData.issue_count" :key="n"
          class="relative card border w-full md:w-fit shadow-md rounded-md flex flex-col items-center" :class="{
            'border-primary': issues[n - 1].have,
            'border-accent': issues[n - 1].read
          }">

          <div class="relative w-full md:h-52 h-40">
            <img :src="imagesrc" alt="Issue Thumbnail"
              class="w-full h-full object-cover rounded-md brightness-80 hover:brightness-100 transition duration-300" />

            <p
              class="absolute inset-0 flex items-center justify-center text-white text-3xl font-bold bg-black/50 rounded-md">
              #{{ n }}
            </p>
          </div>

          <div class="flex w-full justify-around gap-2 text-sm md:text-md md:gap-4 p-4">
            <label class="cursor-pointer flex items-center gap-2"
              :class="issues[n - 1].have ? 'text-primary' : 'text-white'">
              <span>Have</span>
              <input type="checkbox" v-model="issues[n - 1].have" class="checkbox"
                :class="issues[n - 1].have ? 'checkbox-primary' : ''" />
            </label>
            <label class="cursor-pointer flex items-center gap-2"
              :class="issues[n - 1].read ? 'text-green-500' : 'text-white'">
              <span>Read</span>
              <input type="checkbox" v-model="issues[n - 1].read" class="checkbox"
                :class="issues[n - 1].read ? 'checkbox-accent' : ''" />
            </label>
          </div>

          <div class="flex flex-col w-full pb-4 px-4 gap-2 text-sm md:text-md"
            v-if="issues[n - 1].have || issues[n - 1].read">
            <label class="flex flex-col" v-if="issues[n - 1].have">
              <span class="text-white">Purchase Date</span>
              <input type="date" v-model="issues[n - 1].purchaseDate" class="input input-bordered w-full" />
            </label>
            <label class="flex flex-col" v-if="issues[n - 1].read">
              <span class="text-white">Read Date</span>
              <input type="date" v-model="issues[n - 1].readDate" class="input input-bordered w-full" />
            </label>
            <label class="flex flex-col" v-if="issues[n - 1].have">
              <span class="text-white">Price</span>
              <input type="number" v-model="issues[n - 1].price" class="input input-bordered w-full" step="0.01" />
            </label>
          </div>

        </div>
      </div>


      <div class="flex justify-between mt-6">
        <button class="btn btn-danger" @click="showIssueSection = false">Go Back / Cancel</button>
        <button class="btn btn-primary" @click.prevent="createSeries">Create Series</button>
      </div>
    </div> -->

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

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const imageLinkInput = ref("");

const router = useRouter();
const showIssueSection = ref(false);
const readAll = ref(false);
const haveAll = ref(false);
const issues = ref([]);

const seriesData = ref<Partial<Series>>({
  title: '',
  creator: [],
  description: '',
  genre: [],
  main_char: '',
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
    console.log("Title is required!");
    return;
  }

  try {
    // Calculate owned and read counts dynamically based on issues
    const owned_count = issues.value.filter((issue) => issue.have).length;
    const read_count = issues.value.filter((issue) => issue.read).length;
    seriesData.value.issue_count = issues.value.length;

    // Prepare the payload for the series
    const payload = {
      title: seriesData.value.title,
      publisher: seriesData.value.publisher || "",
      creator: seriesData.value.creator || [],
      description: seriesData.value.description || "",
      genre: seriesData.value.genre || [],
      main_char: seriesData.value.main_char || "",
      main_char_type: "character",
      series_format: seriesData.value.series_format || "",
      issue_count: seriesData.value.issue_count || 0,
      read_count: read_count,
      owned_count: owned_count,
    };

    console.log(payload);


    // Append the image if available
    const formData = new FormData();
    for (const key in payload) {
      if (Array.isArray(payload[key])) {
        formData.append(key, JSON.stringify(payload[key]));
      } else {
        formData.append(key, payload[key]?.toString() || "");
      }
    }
    if (seriesData.value.thumbnail) {
      console.log(seriesData.value.thumbnail);

      formData.append("thumbnail", seriesData.value.thumbnail);
    } else {

      console.log("No thumbnail provided.");
    }

    // Send series data to backend
    const response = await SeriesService.addSeries(formData);
    const seriesId = response?.id;

    console.log("Series created successfully!", seriesData.value.issue_count);

    // If there are issues, create them separately
    if (seriesId) {
      await addIssues(response.id);
    } else {
      console.log("Series Creation Failed!");
    }
  } catch (error) {
    console.error("Error creating series:", error);
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
