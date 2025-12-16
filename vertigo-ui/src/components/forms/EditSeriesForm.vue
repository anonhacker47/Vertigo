<template>
    <div v-if="!showIssueSection"
        class="card h-full w-full md:w-2/4 flex gap-8 y-8 shadow-2xl bg-base-100 justify-between p-8">
        <div class="flex pb-4 flex-col w-full md:flex-row gap-8 md:gap-20 justify-around">
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
                <SingleSelectCombobox v-model="localSeriesData.publisher" :items="seriesFieldValues.publisher || []"
                    field="publisher" placeholder="Publisher" />
            </div>
        </div>

        <div class="flex flex-col md:flex-row pb-6 gap-8 md:gap-20 justify-around">
            <div class="form-control w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.genre" :items="seriesFieldValues.genre || []"
                    field="genre" placeholder="Genre" />
                <p v-if="localSeriesData.genre.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
            <div class="form-control w-full text-center">
                <MultiSelectCombobox :items="seriesFieldValues.character || []" v-model="localSeriesData.character"
                    field="character" placeholder="Characters" />
                <p v-if="localSeriesData.genre.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
            <div class="form-control w-full text-center">
                <MultiSelectCombobox v-model="localSeriesData.creator" :items="seriesFieldValues.creator || []"
                    field="creator" placeholder="Creators" />
                <p v-if="localSeriesData.creator.length == 0" class="text-sm text-gray-400 mt-1">You can select multiple
                    options</p>
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-20 justify-around">
            <div class="form-control w-full relative">
                <textarea class="textarea w-full textarea-bordered h-32" placeholder="Summary"
                    v-model="localSeriesData.description" @input="validateDescription"></textarea>
                <p class="text-sm mt-2" :class="{
                    'text-gray-400': descriptionLength <= 1250,
                    'text-red-500': descriptionLength > 1250
                }">
                    {{ descriptionLength }}/1250 characters
                </p>
                <p v-if="descriptionError" class="text-red-500 text-sm absolute bottom-[-1.5rem]">
                    {{ descriptionError }}
                </p>
            </div>
        </div>

        <div class="flex flex-col gap-4 justify-around">
            <div class="flex flex-col md:flex-row gap-8 justify-around ">
                <div class="form-control w-full">
                    <button type="button" @click="$router.back" class="btn btn-dange w-full">
                        Cancel
                    </button>
                </div>
                <div class="form-control w-full">
                    <button @click.prevent="updateSeries"
                        :disabled="!localSeriesData.title || !localSeriesData.series_format"
                        class="btn btn-primary rounded w-full">
                        Save Details
                    </button>
                </div>
            </div>
            <div class="form-control w-full">
                <button @click.prevent="confirmSeriesDelete(localSeriesData.id, localSeriesData.title)"
                    :disabled="!localSeriesData.title || !localSeriesData.series_format"
                    class="btn btn-error rounded w-full">
                    Delete Series
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
import { useRouter } from "vue-router";
import SeriesService from "@/services/SeriesService";
import { useToast } from "primevue/usetoast";
import { useConfirmAction } from "@/composables/useConfirmAction";

const router = useRouter();
const seriesFields = ['publisher', 'genre', 'character', 'creator'];
const seriesFieldValues = ref({});

const { confirmAction } = useConfirmAction();
const toast = useToast();
const message = ref();

const props = defineProps<{
    modelValue: Partial<Series>,
    showIssueSection: boolean
}>()

const emit = defineEmits(['update:modelValue', 'updateSeries'])

const localSeriesData = reactive({ ...props.modelValue })

watch(localSeriesData, (val) => {
    const { thumbnail, ...rest } = val;
    emit('update:modelValue', {
        ...rest,
        thumbnail: props.modelValue.thumbnail, // preserve the original thumbnail
    });
}, { deep: true });

watch(
    () => props.modelValue,
    (newVal) => {
        Object.assign(localSeriesData, newVal);
    },
    { deep: true }
);

const updateSeries = () => {
    emit('updateSeries')
}

const descriptionLength = ref(0);
const descriptionError = ref("");

function validateDescription() {
    descriptionLength.value = localSeriesData.description?.length || 0;

    if (descriptionLength.value > 1250) {
        descriptionError.value = "Description cannot exceed 1250 characters.";
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

const confirmSeriesDelete = (id: number, title: any) => {
    confirmAction({
        message: `Series ${title}`,
        header: "Confirm Deletion",
        acceptLabel: "Delete",
        severity: "danger",
        successMessage: `$Series ${title} deleted`,
        onAccept: () => {
            deleteSeries(id);
            toast.add({
                severity: "success",
                summary: "Confirmed",
                detail: `Series ${title} deleted`,
                life: 3000,
            });
        },
    });
};

async function deleteSeries(id: number) {
    try {
        await SeriesService.removeSeries(id);
        router.push({ name: "Collection" });
    } catch (error) {
        message.value = error;
    }
    console.log(message);
}
</script>