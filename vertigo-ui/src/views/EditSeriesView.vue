<template>
  <form @submit.prevent autocomplete="on" class="flex flex-row">
    <div class="content">
      <div class="card w-[22rem] bg-base-100 shadow-xl">
        <figure class="px-5 pt-5">
          <img :src="imagesrc" @error="changeThumb"  alt="Invalid Link" class="rounded-xl w-[24rem] h-[27rem]"
            key="imagesrc" />
        </figure>
        <div class="flex flex-col p-5" v-if="true">
          <div class="flex flex-col gap-2">
            <div class="form-control w-full">
              <label class="btn btn-primary" for="file">
                Upload Image
              </label>
              <input type="file" @change="changeImage($event,'file')" id="file" accept="image/*" style="display: none" />
            </div>
            <div class="flex justify-center">
              <p class="text-center font-bold">OR</p>
            </div>
            <div class="form-control w-full">
              <input id="image" type="text" v-model="imageLinkInput" @input="changeImage($event,'url')" placeholder="paste image link here"
                class="input input-bordered"  />
            </div>
          </div>
        </div>
      </div>
      <div class="card h-full shadow-2xl bg-base-100">
        <div class="card-body justify-between">
          <div class="flex flex-row gap-16 mb-5 justify-around">
            <div class="form-control max-w-52">
              <input type="text" placeholder="Series Name" v-model="seriesData.title" class="input input-bordered"
                required />
            </div>
            <div class="form-control w-full max-w-52">
              <select class="select select-primary" v-model="seriesData.series_format" required>
                <option disabled value="">Pick Format</option>
                <option>TPB</option>
                <option>HC</option>
                <option>OMNI</option>
                <option>ABS</option>
                <option>MANGA</option>
              </select>
            </div>
            <div class="form-control max-w-52">
              <input type="number" v-model.number="seriesData.issue_count" placeholder="Book Count"
                class="input input-bordered" />
            </div>
          </div>
          <div class="flex flex-row gap-16 mt-5 justify-around">
            <div class="form-control">
              <SingleSelectCombobox v-model="seriesData.publisher" field="publisher" placeholder="Publisher" />
            </div>
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.genre" field="genre" placeholder="Genre" />

            </div>
            <div class="form-control">
              <SingleSelectCombobox v-model="seriesData.main_char" field="main_char"
                placeholder="Main Character/ Team" />

            </div>
          </div>
          <div class="flex flex-row gap-16 justify-around">
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.creator" field="creator" placeholder="Creator" />

            </div>
          </div>
          <div class="flex flex-row gap-16 mb-3 justify-around">
            <div class="form-control w-full">
              <textarea class="textarea textarea-bordered h-24" placeholder="Summary"
                v-model="seriesData.description"></textarea>
            </div>
          </div>
          <div class="flex flex-row gap-16 mb-3 justify-around">
            <div class="form-control w-full">
              <div class="form-control">
                <label class="label cursor-pointer">
                  <span class="text-emerald-400">Read Already?</span>
                  <input type="checkbox" true-value="1" false-value="0" v-model.number="seriesData.read_count"
                    class="checkbox checkbox-accent" />
                </label>
              </div>
            </div>
            <div class="form-control w-full">
              <div class="form-control">
                <label class="label cursor-pointer">
                  <span class="text-emerald-400">All Bought?</span>
                  <input type="checkbox" true-value="1" false-value="0" v-model.number="seriesData.owned_count"
                    class="checkbox checkbox-accent" />
                </label>
              </div>
            </div>
          </div>
          <div class="flex flex-row gap-16 justify-around">
            <div class="form-control w-full">
              <button @click="updateSeries" class="btn btn-primary">
                Update Series
              </button>
            </div>
            <div class="form-control w-full">
              <button type="button" @click="router.back" class="btn btn-danger">
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import type { Series } from "@/types/series.types";

import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";
import SingleSelectCombobox from "../components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "../components/customInputs/MultiSelectCombobox.vue";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const router = useRouter();
const route = useRoute();

const seriesId = Number(route.params.Id);

const imageLinkInput = ref("");

async function getSeries() {
  try {
    const response = await SeriesService.getSeriesbyId(seriesId)
    Object.assign(seriesData, response);
    console.log(seriesData);    
    imagesrc.value = `${SeriesService.getImagebyId(seriesId)}?t=${Date.now()}`
    } catch (error) {
    console.log(error);
  }
}

const seriesData: Partial<Series> = reactive({
  title: "",
  creator: [],
  description: "",
  genre: [],
  publisher: "",
  main_char: "",
  series_format: "",
  issue_count: 0,
  thumbnail: "",
  read_count: 0,
  owned_count: 0,
});

onMounted(() => {
  getSeries();
});


function changeImage(event: any, inputType: string) {
  
  const file = event.target.files && event.target.files[0]
  ? URL.createObjectURL(event.target.files[0])
  : "";
  
  let newValue: string = "";
  if (inputType === "file") {
    newValue = file;
    imageLinkInput.value = event.target.value
  } else if (inputType === "url") {
    newValue = event.target.value || new URL("../assets/dummy.webp", import.meta.url).href;
  }
  
  imagesrc.value = newValue;
  console.log(imagesrc.value );
  seriesData.thumbnail = event.target.files ? event.target.files[0] : "noimage";
}

function changeThumb() {
  seriesData.thumbnail = "noimage";
}

async function updateSeries() {
  try {
    const owned_count = seriesData.owned_count == 1 ? seriesData.issue_count : 0;
    const read_count = seriesData.read_count == 1 ? seriesData.issue_count : 0;

    // Create a FormData object
    const formData = new FormData();
    formData.append("title", seriesData.title || "");
    formData.append("publisher", seriesData.publisher || "");
    formData.append("creator", JSON.stringify(seriesData.creator || []));
    formData.append("description", seriesData.description || "");
    formData.append("genre", JSON.stringify(seriesData.genre || []));
    formData.append("main_char", seriesData.main_char || "");
    formData.append("main_char_type", "character");
    formData.append("series_format", seriesData.series_format || "");
    formData.append("issue_count", seriesData.issue_count?.toString() || "0");
    formData.append("read_count", read_count.toString());
    formData.append("owned_count", owned_count.toString());

    // Append the image file if it exists
    if (seriesData.thumbnail && typeof seriesData.thumbnail !== "string") {
      formData.append("thumbnail", seriesData.thumbnail);
    }

    console.log(formData);
    

    // Send the FormData to the backend
    await SeriesService.updateSeries(seriesId,formData).then((response) => {
      router.push({name: 'SeriesDetail', params: {Id: String(response.data.id), Link: response.data.link}})
    });

  } catch (error) {
    console.log(error);
  }
}


</script>

<style scoped>
.content {
  z-index: 0;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  gap: 1rem;
  padding: 1rem;
  flex: 1;
}

.card-body {
  gap: 0 !important;
}

img {
  color: red;
  font-size: x-large;
  text-align: center;
}
</style>
