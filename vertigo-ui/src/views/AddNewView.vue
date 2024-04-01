<template>
  <HeaderItem />
  <form @submit.prevent autocomplete="on" class="flex flex-row">
    <div class="content">
      <div class="card w-[22rem] bg-base-100 shadow-xl">
        <figure class="px-5 pt-5">
          <img :src="imagesrc" @error="changeThumb" alt="Invalid Image Link" class="rounded-xl w-[26rem] h-[29rem]"
            key="imagesrc" />
        </figure>
        <div class="flex flex-col p-5">
          <label class="label justify-center">
            <span class="label-text">Cover Image</span>
          </label>
          <input type="text" @input="changeImage" placeholder="paste image link here" class="input input-bordered"
            required />
        </div>
      </div>
      <div class="card h-full shadow-2xl bg-base-100">
        <div class="card-body justify-between">
          <div class="flex flex-row gap-16 mb-5 justify-around">
            <div class="form-control">
              <input type="text" placeholder="Series Name" v-model="title" class="input input-bordered" required />
            </div>
            <div class="form-control w-full">
              <select class="select select-primary" v-model="series_format" required>
                <option disabled value="">Pick Format</option>
                <option>TPB</option>
                <option>HC</option>
                <option>OMNI</option>
                <option>ABS</option>
                <option>MANGA</option>
              </select>
            </div>
            <div class="form-control">
              <input type="number" v-model.number="issue_count" placeholder="Book Count" class="input input-bordered" />
            </div>
          </div>
          <div class="flex flex-row gap-16 my-5 justify-around">
            <div class="form-control">
              <!-- <input
                type="text"
                placeholder="Publisher"
                v-model="publisher"
                class="input input-bordered"
              /> -->
              <SingleSelectCombobox v-model="publisher" field="publisher" placeholder="Publisher"/>
            </div>
            <div class="form-control">
              <!-- <input type="text" placeholder="Genre" v-model="genre" class="input input-bordered" /> -->
              <SingleSelectCombobox v-model="genre" field="genre" placeholder="Genre"/>

            </div>
            <div class="form-control">
              <!-- <input type="text" v-model="main_char" placeholder="Main Character/Team" class="input input-bordered" /> -->
              <SingleSelectCombobox v-model="main_char" field="main_char" placeholder="Main Character/ Team"/>

            </div>
          </div>
          <div class="flex flex-row gap-16 my-5 justify-around">
            <div class="form-control">
              <!-- <input type="text" placeholder="Writer" v-model="writer" class="input input-bordered" /> -->
              <SingleSelectCombobox v-model="writer" field="writer" placeholder="Writer"/>

            </div>
            <div class="form-control">
              <!-- <input type="text" v-model="artist" placeholder="Artist" class="input input-bordered" /> -->
              <SingleSelectCombobox v-model="artist" field="artist" placeholder="Artist"/>
            </div>
            <div class="form-control">
              <!-- <input type="text" v-model="editor" placeholder="Editor" class="input input-bordered" /> -->
              <SingleSelectCombobox v-model="editor" field="editor" placeholder="Editor"/>

            </div>
          </div>
          <div class="flex flex-row gap-16 mb-3 justify-around">
            <div class="form-control w-full">
              <textarea class="textarea textarea-bordered h-24" placeholder="Summary" v-model="summary"></textarea>
            </div>
          </div>
          <div class="flex flex-row gap-16 mb-3 justify-around">
            <div class="form-control w-full">
              <div class="form-control">
                <label class="label cursor-pointer">
                  <span class="text-emerald-400">Read Already?</span>
                  <input type="checkbox" true-value="1" false-value="0" v-model.number="read_whole"
                    class="checkbox checkbox-accent" />
                </label>
              </div>
            </div>
            <div class="form-control w-full">
              <div class="form-control">
                <label class="label cursor-pointer">
                  <span class="text-emerald-400">All Bought?</span>
                  <input type="checkbox" true-value="1" false-value="0" v-model.number="have_whole"
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

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import HeaderItem from "../components/HeaderItem.vue";
import IssueService from "../services/IssueService";
import SeriesService from "../services/SeriesService";
import SingleSelectCombobox from "../components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "../components/customInputs/MultiSelectCombobox.vue";

const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const router = useRouter();

const title = ref("");
const publisher = ref("");
const writer = ref("");
const artist = ref("");
const editor = ref("");
const summary = ref("");
const genre = ref([]);
const main_char = ref("");
const series_format = ref("");
const issue_count = ref(0);
const read_whole = ref(0);
const have_whole = ref(0);
const thumbnail = ref("");


function changeImage(event) {
  event.target.value
    ? (imagesrc.value = event.target.value)
    : (imagesrc.value = new URL("../assets/dummy.webp", import.meta.url).href);
  thumbnail.value = event.target.value;
}

function changeThumb() {
  thumbnail.value = "noimage";
}

async function createSeries() {

  try {
    const have_count = have_whole.value == 1 ? issue_count.value : 0;
    const read_count = read_whole.value == 1 ? issue_count.value : 0;
    console.log("have_count", have_count);
    console.log("read_count", read_count);
    const response = await SeriesService.addSeries(
      {
        title: title.value,
        publisher: publisher.value,
        writer: writer.value,
        artist: artist.value,
        editor: editor.value,
        summary: summary.value,
        genre: genre.value,
        main_char: main_char.value,
        series_format: series_format.value,
        issue_count: issue_count.value,
        read_count: read_count,
        have_count: have_count,
        thumbnail: thumbnail.value,
      },
    );
    if (issue_count.value > 0) {
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
        read_whole: 1,
        have_whole: 1,
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
