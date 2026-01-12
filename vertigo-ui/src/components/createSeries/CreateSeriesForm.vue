<template>
    <div v-if="!showIssueSection" class="card h-full w-full flex gap-8 y-8 shadow-2xl bg-base-100 justify-between p-8">
        <div class="flex pb-4 flex-col w-full md:flex-row gap-6 md:gap-20 justify-around">
            <div class=" w-full">
                <input type="text" placeholder="Series Name" v-model="localSeriesData.title"
                    class="input w-full input-bordered" required />
            </div>
            <div class=" w-full">
                <select class="select  w-full select-primary" v-model="localSeriesData.series_format" required>
                    <option disabled value="">Pick Format</option>
                    <option>Single Issues</option>
                    <option>Trade Paperback</option>
                    <option>Hard Cover</option>
                    <option>Omnibus</option>
                    <option>Absolute Edition</option>
                </select>
            </div>
            <div class=" w-full">
                <SingleSelectCombobox v-model="localSeriesData.publisher" :items="seriesFieldValues.publisher || []"
                    field="publisher" placeholder="Publisher" />
            </div>
        </div>

        <div class="flex flex-col md:flex-row pb-4 gap-6 md:gap-20 justify-around">
            <div class=" w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.genre" :items="seriesFieldValues.genre || []"
                    field="genre" placeholder="Select Genre(s)" />
                <p v-if="localSeriesData.genre.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
            <div class=" w-full text-center">
                <MultiSelectCombobox :items="seriesFieldValues.character || []" v-model="localSeriesData.character"
                    field="character" placeholder="Characters" />
                <p v-if="localSeriesData.genre.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
            <div class=" w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.creator" :items="seriesFieldValues.creator || []"
                    field="creator" placeholder="Select Creator(s)" />
                <p v-if="localSeriesData.creator.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
        </div>

        <div class="flex flex-col md:flex-row justify-around">
            <div class=" w-full relative">
                <textarea class="textarea textarea-bordered h-36 w-full" placeholder="Summary"
                    v-model="localSeriesData.description" @input="validateDescription"></textarea>
                <p class="text-sm mt-2" :class="{
                    'text-gray-400': descriptionLength <= 3000,
                    'text-red-500': descriptionLength > 3000
                }">
                    {{ descriptionLength }}/3000 characters
                </p>
                <p v-if="descriptionError" class="text-red-500 text-sm absolute bottom-[-1.5rem]">
                    {{ descriptionError }}
                </p>
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-16 justify-around">
            <div class=" w-full">
                <button type="button" @click="$router.push('/collection')" class="btn btn-danger w-full">
                    Cancel
                </button>
            </div>
            <div class=" w-full">
                <button @click.prevent="goToNext" :disabled="!localSeriesData.title || !localSeriesData.series_format"
                    class="btn btn-primary rounded w-full">
                    Next
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Series } from "@/types/series.types";
import { onMounted, reactive, ref, watch } from 'vue'
import SingleSelectCombobox from "@/components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "@/components/customInputs/MultiSelectCombobox.vue";
import SeriesService from "@/services/SeriesService";

const seriesFields = ['publisher', 'genre', 'character', 'creator'];
const seriesFieldValues = ref({});
const descriptionLength = ref(0);
const descriptionError = ref("");

const props = defineProps<{
    modelValue: Partial<Series>,
    showIssueSection: boolean
}>()

const emit = defineEmits(['update:modelValue', 'next'])

const localSeriesData = reactive({ ...props.modelValue })

watch(
    () => props.modelValue,
    (newVal) => {
        Object.assign(localSeriesData, newVal)
    },
    { deep: true }
)

watch(localSeriesData, (val) => {
    const { thumbnail, ...rest } = val;
    emit('update:modelValue', {
        ...rest,
        thumbnail: props.modelValue.thumbnail, // preserve the original thumbnail
    });    
}, { deep: true });

watch(
  () => localSeriesData.description,
  (val) => {
    descriptionLength.value = val?.length || 0;
    descriptionError.value = descriptionLength.value > 3000 ? "Description cannot exceed 3000 characters." : "";
  },
  { immediate: true }
);

const goToNext = () => {
    emit('next')
}


function validateDescription() {
    descriptionLength.value = localSeriesData.description?.length || 0;

    if (descriptionLength.value > 3000) {
        descriptionError.value = "Description cannot exceed 3000 characters.";
    } else {
        descriptionError.value = "";
    }
}

onMounted(() => {
    getSeriesFields();
});

async function getSeriesFields() {
    try {

        for (const field of seriesFields) {
            const response = await SeriesService.getSeriesFieldValues(field);
            seriesFieldValues.value[field] = response.data;
        }
    } catch (error) {
        console.log(error);
    }
}


</script>