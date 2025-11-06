<template>
    <div class="flex md:flex-row flex-col items-center justify-between gap-3 py-6 w-full max-w-6xl mx-auto"> <!-- Search Input -->
        <InputText v-model="searchQuery" placeholder="Search series..." class="w-full md:w-52"
            @keyup.enter="applySearch" />

        <!-- Filters -->
        <Dropdown v-model="selectedPublisher" :options="items.publisher" optionLabel="value" placeholder="Publisher"
            class="w-full md:w-52" scrollHeight="200px" showClear />

        <!-- Creator -->
        <Dropdown v-model="selectedCreator" :options="items.creator" optionLabel="value" placeholder="Creator"
            class="w-full md:w-44" scrollHeight="200px" showClear />

        <!-- Genre -->
        <Dropdown v-model="selectedGenre" :options="items.genre" optionLabel="value" placeholder="Genre"
            class="w-full md:w-40" scrollHeight="200px" showClear />

        <!-- Format -->
        <Dropdown v-model="selectedFormat" :options="items.series_format" placeholder="Format" class="w-full md:w-32"
            scrollHeight="200px" showClear />

        <!-- Buttons -->
        <Button label="Search" icon="pi pi-search" class="p-button-info w-32" @click="applySearch" />
        <Button v-if="isSearched" label="Reset" icon="pi pi-times" class="p-button-danger w-32" @click="resetSearch" />
    </div>
</template>

<script setup>
import SeriesService from "@/services/SeriesService";
import { ref, computed, defineEmits, onMounted } from "vue";
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

const emit = defineEmits(["search"]); // emit event to parent

const searchQuery = ref("");
const selectedGenre = ref("");
const selectedCreator = ref("");
const selectedFormat = ref("");
const selectedPublisher = ref("");

// optional: emit search whenever any input changes
const applySearch = () => {
    emit("search", {
        query: searchQuery.value,
        genre: selectedGenre.value,
        creator: selectedCreator.value,
        publisher: selectedPublisher.value,
        series_format: selectedFormat.value,
    });
};

const isSearched = computed(() => {
    return (
        searchQuery.value ||
        selectedGenre.value ||
        selectedCreator.value ||
        selectedFormat.value ||
        selectedPublisher.value
    );
});

const resetSearch = () => {
    searchQuery.value = "";
    selectedGenre.value = "";
    selectedCreator.value = "";
    selectedFormat.value = "";
    selectedPublisher.value = "";

    // Emit an empty search so parent knows to reset
    emit("search", {
        query: "",
        genre: "",
        creator: "",
        publisher: "",
        series_format: "",
    });
};

const fields = ref(['publisher', 'creator', 'genre', 'series_format']);
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

<style scoped></style>