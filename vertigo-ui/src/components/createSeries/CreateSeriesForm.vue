<template>
    <div v-if="!showIssueSection"
        class="card h-full w-full md:w-2/3 flex gap-6 md:gap-10 shadow-2xl bg-base-100 justify-between p-8">
        <div class="flex flex-col w-full md:flex-row gap-8 md:gap-20 justify-around">
            <div class="form-control w-full">
                <input type="text" placeholder="Series Name" v-model="localSeriesData.title"
                    class="input w-full input-bordered" required />
            </div>
            <div class="form-control w-full">
                <select class="select  w-full select-primary" v-model="localSeriesData.series_format" required>
                    <option disabled value="">Pick Format</option>
                    <option>Single Issues</option>
                    <option>Trade Paperback</option>
                    <option>Hard Cover</option>
                    <option>Omnibus</option>
                    <option>Absolute Edition</option>
                    <option>Manga</option>
                </select>
            </div>
            <div class="form-control w-full">
                <SingleSelectCombobox v-model="localSeriesData.publisher" field="publisher" placeholder="Publisher" />
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-8 md:gap-20 justify-around">
            <div class="form-control w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.genre" field="genre" placeholder="Select Genre(s)" />
                <p v-if="localSeriesData.genre.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple options</p>
            </div>
            <div class="form-control w-full">
                <SingleSelectCombobox v-model="localSeriesData.main_character" field="main_character"
                    placeholder="Main Character/ Team" />
            </div>
            <div class="form-control w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.creator" field="creator" placeholder="Select Creator(s)" />
                <p v-if="localSeriesData.creator.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple options</p>
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-20 justify-around">
            <div class="form-control w-full">
                <textarea class="textarea textarea-bordered" placeholder="Summary"
                    v-model="localSeriesData.description"></textarea>
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-16 justify-around">
            <div class="form-control w-full">
                <button type="button" @click="$router.push('collection')" class="btn btn-danger">
                    Cancel
                </button>
            </div>
            <div class="form-control w-full">
                <button @click.prevent="goToNext" :disabled="!localSeriesData.title || !localSeriesData.series_format" class="btn btn-primary rounded">
                    Next
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Series } from "@/types/series.types";
import {  reactive, watch } from 'vue'
import SingleSelectCombobox from "@/components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "@/components/customInputs/MultiSelectCombobox.vue";



const props = defineProps<{
  modelValue: Partial<Series>,
  showIssueSection: boolean
}>()

const emit = defineEmits(['update:modelValue', 'next'])

const localSeriesData = reactive({ ...props.modelValue })

watch(localSeriesData, (val) => {
  const { thumbnail, ...rest } = val;
  emit('update:modelValue', {
    ...rest,
    thumbnail: props.modelValue.thumbnail, // preserve the original thumbnail
  });
}, { deep: true });

const goToNext = () => {
  emit('next')
}

</script>