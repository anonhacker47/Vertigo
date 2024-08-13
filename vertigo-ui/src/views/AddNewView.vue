<template>
  <form @submit.prevent autocomplete="on" class="flex flex-row">
    <div class="content">
      <div class="card w-[22rem] bg-base-100 shadow-xl">
        <figure class="px-5 pt-5">
          <img :src="imagesrc" @error="changeThumb" alt="Invalid Link" class="rounded-xl w-[26rem] h-[29rem]"
            key="imagesrc" />
        </figure>
        <div class="flex flex-col p-5">
          <label class="label justify-center" for="image">
            <span class="label-text">Cover Image</span>
          </label>
          <input id="image" type="text" @input="changeImage" placeholder="paste image link here" class="input input-bordered"
            required />
        </div>
      </div>
      <div class="card h-full shadow-2xl bg-base-100">
        <div class="card-body justify-between">
          <div class="flex flex-row gap-16 mb-5 justify-around">
            <div class="form-control max-w-52">
              <input type="text" placeholder="Series Name" v-model="seriesData.title" class="input input-bordered" required />
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
              <input type="number" v-model.number="seriesData.issue_count" placeholder="Book Count" class="input input-bordered" />
            </div>
          </div>
          <div class="flex flex-row gap-16 mt-5 justify-around">
            <div class="form-control">
              <SingleSelectCombobox v-model="publisherList" field="publisher" placeholder="Publisher"/>
            </div>
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.genre" field="genre" placeholder="Genre"/>

            </div>
            <div class="form-control">
              <SingleSelectCombobox v-model="seriesData.main_char" field="main_char" placeholder="Main Character/ Team"/>

            </div>
          </div>
          <div class="flex flex-row gap-16 justify-around">
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.writer" field="writer" placeholder="Writer"/>

            </div>
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.artist" field="artist" placeholder="Artist"/>
            </div>
            <div class="form-control">
              <MultiSelectCombobox v-model="seriesData.editor" field="editor" placeholder="Editor"/>

            </div>
          </div>
          <div class="flex flex-row gap-16 mb-3 justify-around">
            <div class="form-control w-full">
              <textarea class="textarea textarea-bordered h-24" placeholder="Summary" v-model="seriesData.description"></textarea>
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
              <button @click="createSeries" class="btn btn-primary">
                Add Series
              </button>
            </div>
            <div class="form-control w-full">
              <button type="button" @click="router.push('collection')" class="btn btn-danger">
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
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";

import type { Series } from "@/types/series.types";

import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";
import SingleSelectCombobox from "../components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "../components/customInputs/MultiSelectCombobox.vue";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const router = useRouter();

const seriesData: Partial<Series> = reactive({
  title: "",
  writer: [],
  artist: [],
  editor: [],
  description: "",
  genre: [],
  main_char: "",
  series_format: "",
  issue_count: 0,
  thumbnail: "",
  read_count: 0,
  owned_count: 0,
});

const publisherList = ref<string>("");

function changeImage(event) {
  event.target.value
    ? (imagesrc.value = event.target.value)
    : (imagesrc.value = new URL("../assets/dummy.webp", import.meta.url).href);
    seriesData.thumbnail = event.target.value;
}

function changeThumb() {
  seriesData.thumbnail = "noimage";
}

async function createSeries() {

  try {
    const owned_count = seriesData.owned_count == 1 ? seriesData.issue_count : 0;
    const read_count = seriesData.read_count == 1 ? seriesData.issue_count : 0;
    console.log("owned_count", owned_count);
    console.log("read_count", read_count);

    const response = await SeriesService.addSeries(
      {
        title: seriesData.title,
        publisher: [publisherList.value],
        writer: seriesData.writer,
        artist: seriesData.artist,
        editor: seriesData.editor,
        description: seriesData.description,
        genre: seriesData.genre,
        main_char: seriesData.main_char,
        main_char_type: "character",
        series_format: seriesData.series_format,
        issue_count: seriesData.issue_count,
        read_count: read_count,
        owned_count: owned_count,
        thumbnail: seriesData.thumbnail,
      },
    );
    if (seriesData.issue_count > 0) {
      addIssues();
    } else {
      console.log("nothing to add");
    }
    // router.push("home");
  } catch (error) {
    console.log(error);
  }
}

async function getPrimaryKey() {
  try {
    const response = await SeriesService.getSeriesKey();

    const key = response.data;

    return key;
  } catch (error) {
    console.log(error);
  }
}

async function addIssues() {
  var key = await getPrimaryKey();
  try {
    const response = await IssueService.addIssues(
      key,
      {
        title: "title",
        is_read: 1,
        is_owned: 1,
      },
    );
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
