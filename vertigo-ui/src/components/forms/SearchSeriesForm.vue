<template>
    <div class="flex md:flex-row flex-col items-center justify-between gap-3 w-full max-w-7xl mx-auto px-4">
        <InputText v-model="searchQuery" placeholder="Search Series..." class="w-full md:w-52"
            @keyup.enter="applySearch" />

        <Select v-model="selectedPublisher" :options="items.publisher" @change="applySearch" optionLabel="value"
            placeholder="Publisher" class="w-full md:w-52" scrollHeight="200px" showClear />

        <Select v-model="selectedCreator" :options="items.creator" @change="applySearch" optionLabel="value"
            placeholder="Creator" class="w-full md:w-44 bg-base-100" scrollHeight="200px" showClear />


        <Select v-model="selectedCharacter" :options="items.character" @change="applySearch" optionLabel="value"
            placeholder="Character" class="w-full md:w-44" scrollHeight="200px" showClear />


        <Select v-model="selectedGenre" :options="items.genre" @change="applySearch" optionLabel="value"
            placeholder="Genre" class="w-full md:w-40" scrollHeight="200px" showClear />

        <Select v-model="selectedFormat" :options="items.series_format"  @change="applySearch" placeholder="Format"
            class="w-full md:w-32" scrollHeight="200px" showClear />

        <Button label="Search" icon="pi pi-search" class="p-button-info w-full md:w-32" @click="applySearch" />
        <Button v-if="isSearched" label="Reset" icon="pi pi-times" class="p-button-danger w-full md:w-32"
            @click="resetSearch" />
    </div>
</template>

<script setup lang="ts">
import SeriesService from "@/services/SeriesService";
import { ref, computed, onMounted, watch } from "vue";
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Select from 'primevue/select';

const emit = defineEmits(["search"]);

const props = defineProps<{
    initialFilters: {
        query?: string
        genre?: string
        creator?: string
        publisher?: string
        character?: string
        series_format?: string
    }
}>()

const searchQuery = ref("");
const selectedGenre = ref(null);
const selectedCreator = ref(null);
const selectedCharacter = ref(null);
const selectedFormat = ref(null);
const selectedPublisher = ref(null);


const fields = ref(['publisher', 'creator', 'genre', 'series_format', 'character']);
const items = ref({});

const findOption = (list, value) => {
    return list?.find(item => item.value === value) || null
}

watch(
    () => props.initialFilters,
    (filters) => {
        searchQuery.value = filters.query || ""

        selectedPublisher.value = findOption(items.value.publisher, filters.publisher)
        selectedCreator.value = findOption(items.value.creator, filters.creator)
        selectedCharacter.value = findOption(items.value.character, filters.character)
        selectedGenre.value = findOption(items.value.genre, filters.genre)
        selectedFormat.value = filters.series_format || null
    },
    { immediate: true }
)

const applySearch = () => {
    emit("search", {
        query: searchQuery.value || "",
        genre: selectedGenre.value?.value || "",
        creator: selectedCreator.value?.value || "",
        character: selectedCharacter.value?.value || "",
        publisher: selectedPublisher.value?.value || "",
        series_format: selectedFormat.value || "",
    });
};

const isSearched = computed(() => {
    return Boolean(
        searchQuery.value ||
        selectedGenre.value ||
        selectedCreator.value ||
        selectedFormat.value ||
        selectedPublisher.value ||
        selectedCharacter.value
    );
});

const resetSearch = () => {
    searchQuery.value = "";
    selectedGenre.value = null;
    selectedCreator.value = null;
    selectedCharacter.value = null;
    selectedFormat.value = null;
    selectedPublisher.value = null;

    emit("search", {
        query: "",
        genre: "",
        creator: "",
        charachter: "",
        publisher: "",
        series_format: "",
    });
};

async function getSeriesFields() {
    try {
        for (const field of fields.value) {
            const response = await SeriesService.getSeriesFieldValues(field)
            items.value[field] = response.data
        }

        // 🔥 Sync once options exist
        if (props.initialFilters) {
            searchQuery.value = props.initialFilters.query || ""

            selectedPublisher.value = findOption(items.value.publisher, props.initialFilters.publisher)
            selectedCreator.value = findOption(items.value.creator, props.initialFilters.creator)
            selectedCharacter.value = findOption(items.value.character, props.initialFilters.character)
            selectedGenre.value = findOption(items.value.genre, props.initialFilters.genre)
            selectedFormat.value = props.initialFilters.series_format || null
        }
    } catch (error) {
        console.log(error)
    }
}

onMounted(() => {
    getSeriesFields();
});

</script>

<style scoped>
    
</style>