<template>
    <div class="flex flex-col md:flex-row items-center md:justify-between gap-3 py-6 w-full max-w-4xl mx-auto">
        <!-- Search Input -->
        <input v-model="searchQuery" type="text" placeholder="Search series..."
            class="input input-bordered rounded-md  flex-1" @keyup.enter="applySearch" />

        <!-- Filters -->
        <div class="flex flex-wrap md:flex-nowrap items-center gap-2 w-full md:w-auto">
            <select v-model="selectedPublisher" class="select select-bordered rounded-md w-full md:w-36">
                <option disabled value="">Publisher</option>
                <option v-for="item in items['publisher']" :key="item">{{ item.value }}</option>
            </select>

            <select v-model="selectedFormat" class="select select-bordered rounded-md w-full md:w-36">
                <option disabled value="">Format</option>
                <option v-for="item in items['series_format']" :key="item">{{ item }}</option>
            </select>

            <select v-model="selectedGenre" class="select select-bordered rounded-md w-full md:w-36">
                <option disabled value="">Genre</option>
                <option v-for="item in items['genre']" :key="item">{{ item.value }}</option>
            </select>

            <!-- Single Search Button -->
            <button @click="applySearch" class="btn btn-primary rounded-md px-4">Search</button>
            <button @click="resetSearch" v-if="isSearched" class="btn btn-danger rounded-md px-4">Reset</button>
        </div>
    </div>

</template>

<script setup>
import SeriesService from "@/services/SeriesService";
import { ref, computed, defineEmits, onMounted } from "vue";

const emit = defineEmits(["search"]); // emit event to parent

const searchQuery = ref("");
const selectedGenre = ref("");
const selectedFormat = ref("");
const selectedPublisher = ref("");

// optional: emit search whenever any input changes
const applySearch = () => {
    emit("search", {
        query: searchQuery.value,
        genre: selectedGenre.value,
        publisher: selectedPublisher.value,
        series_format: selectedFormat.value,
    });
};

const isSearched = computed(() => {
    return (
        searchQuery.value ||
        selectedGenre.value ||
        selectedFormat.value ||
        selectedPublisher.value
    );
});

const resetSearch = () => {
    searchQuery.value = "";
    selectedGenre.value = "";
    selectedFormat.value = "";
    selectedPublisher.value = "";

    // Emit an empty search so parent knows to reset
    emit("search", {
        query: "",
        genre: "",
        publisher: "",
        series_format: "",
    });
};

const fields = ref(['publisher', 'genre', 'series_format']);
const items = ref({});

async function getSeriesFields() {
    try {

        for (const field of fields.value) {
            await SeriesService.getSeriesFieldValues(field).then((response) => {
                items.value[field] = response.data;
                console.log(items);
            });
        }

        console.log("items2multiple", items.value);
    } catch (error) {
        console.log(error);
    }
}

onMounted(() => {
    getSeriesFields();
});

</script>
