<template>
  <section class="fm-section" aria-labelledby="details-title">
    <div class="fm-section__head">
      <h2 id="details-title" class="fm-section__title">Details</h2>
      <a
        v-if="!metronEditable && localSeriesData.metron_url"
        :href="localSeriesData.metron_url"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-1.5 text-[13px] font-bold text-sky-400 hover:text-sky-300"
      >
        Linked to Metron
        <i class="pi pi-external-link" style="font-size: 11px"></i>
      </a>
      <p v-else class="fm-hint">Title and format are required.</p>
    </div>

    <div class="mt-5 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
      <div>
        <label for="series-title" class="fm-label">Title</label>
        <input
          id="series-title"
          v-model="localSeriesData.title"
          type="text"
          class="fm-input"
          placeholder="Watchmen"
          autocomplete="off"
          :aria-invalid="!!errors?.title || undefined"
          :aria-describedby="errors?.title ? 'series-title-error' : undefined"
        />
        <Message v-if="errors?.title" id="series-title-error" severity="error" size="small" variant="simple" class="mt-1.5">{{ errors.title }}</Message>
      </div>

      <div>
        <label for="series-format" class="fm-label">Format</label>
        <Select
          v-model="localSeriesData.series_format"
          input-id="series-format"
          :options="FORMATS"
          placeholder="Choose a format"
          fluid
          :invalid="!!errors?.series_format"
          :aria-describedby="errors?.series_format ? 'series-format-error' : undefined"
        />
        <Message v-if="errors?.series_format" id="series-format-error" severity="error" size="small" variant="simple" class="mt-1.5">{{ errors.series_format }}</Message>
      </div>

      <div>
        <label for="series-publisher" class="fm-label">Publisher</label>
        <SingleSelectCombobox
          v-model="localSeriesData.publisher"
          input-id="series-publisher"
          :items="fieldValues.publisher || []"
          field="publisher"
          placeholder="Choose or add a publisher"
        />
      </div>

      <div>
        <label for="series-genres" class="fm-label">Genres</label>
        <MultiSelectCombobox
          v-model="localSeriesData.genre"
          input-id="series-genres"
          :items="fieldValues.genre || []"
          field="genre"
          placeholder="Add genres"
        />
      </div>

      <div>
        <label for="series-characters" class="fm-label">Characters</label>
        <MultiSelectCombobox
          v-model="localSeriesData.character"
          input-id="series-characters"
          :items="fieldValues.character || []"
          field="character"
          placeholder="Add characters"
        />
      </div>

      <div>
        <label for="series-creators" class="fm-label">Creators</label>
        <MultiSelectCombobox
          v-model="localSeriesData.creator"
          input-id="series-creators"
          :items="fieldValues.creator || []"
          field="creator"
          placeholder="Add creators"
        />
      </div>

      <template v-if="metronEditable && !localSeriesData.manga">
        <div>
          <label for="series-metron-id" class="fm-label">Metron ID</label>
          <InputNumber v-model="localSeriesData.metron_id" input-id="series-metron-id" :min="0" :use-grouping="false" fluid placeholder="Leave empty to unlink" />
        </div>
        <div class="sm:col-span-1 xl:col-span-2">
          <label for="series-metron-url" class="fm-label">Metron URL</label>
          <input id="series-metron-url" v-model.trim="localSeriesData.metron_url" type="url" class="fm-input" placeholder="https://metron.cloud/series/" />
        </div>
      </template>

      <div class="fm-textbox sm:col-span-2" :data-invalid="tooLong || undefined">
        <div class="fm-textbox__head">
          <label for="series-summary" class="fm-label">Description</label>
          <span class="fm-hint tabular-nums" :class="{ 'fm-hint--error': tooLong }">{{ descriptionLength }} / {{ MAX_TEXT }}</span>
        </div>
        <textarea
          id="series-summary"
          v-model="localSeriesData.description"
          class="fm-textbox__area"
          rows="6"
          placeholder="General description"
          :aria-invalid="tooLong || undefined"
        ></textarea>
        <Message v-if="tooLong" severity="error" size="small" variant="simple" class="fm-textbox__foot">Keep the description under {{ MAX_TEXT }} characters.</Message>
      </div>

      <div class="fm-textbox sm:col-span-2 xl:col-span-1" :data-invalid="notesTooLong || undefined">
        <div class="fm-textbox__head">
          <label for="series-notes" class="fm-label">Notes</label>
          <span class="fm-hint tabular-nums" :class="{ 'fm-hint--error': notesTooLong }">{{ notesLength }} / {{ MAX_TEXT }}</span>
        </div>
        <textarea
          id="series-notes"
          v-model="localSeriesData.notes"
          class="fm-textbox__area"
          rows="6"
          placeholder="Notes for your own reference"
          :aria-invalid="notesTooLong || undefined"
        ></textarea>
        <Message v-if="notesTooLong" severity="error" size="small" variant="simple" class="fm-textbox__foot">Keep notes under {{ MAX_TEXT }} characters.</Message>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Series } from "@/types/series.types";
import { computed, onMounted, ref, watch } from "vue";
import SingleSelectCombobox from "@/components/customInputs/SingleSelectCombobox.vue";
import MultiSelectCombobox from "@/components/customInputs/MultiSelectCombobox.vue";
import SeriesService from "@/services/SeriesService";
import InputNumber from "primevue/inputnumber";
import Message from "primevue/message";
import Select from "primevue/select";

export interface SeriesFormErrors {
  title?: string;
  series_format?: string;
}

const FORMATS = ["Single Issues", "Trade Paperback", "Hard Cover", "Omnibus", "Absolute Edition", "Manga"];
const MAX_TEXT = 3000;
const seriesFields = ["publisher", "genre", "character", "creator"] as const;

const props = defineProps<{
  modelValue: Partial<Series>;
  errors?: SeriesFormErrors;
  /** Edit page: expose the Metron id and URL as inputs. The create page links to Metron instead. */
  metronEditable?: boolean;
}>();

const emit = defineEmits<{ (e: "update:modelValue", value: Partial<Series>): void }>();

const fieldValues = ref<Record<string, any[]>>({});
const localSeriesData = ref<any>({ ...props.modelValue });

watch(
  () => props.modelValue,
  (newVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(localSeriesData.value)) {
      localSeriesData.value = { ...newVal };
    }
  },
  { deep: true }
);

watch(
  localSeriesData,
  (val) => {
    const { thumbnail, ...rest } = val;
    const outgoing = { ...rest, thumbnail: props.modelValue.thumbnail };
    if (JSON.stringify(outgoing) === JSON.stringify(props.modelValue)) return;
    emit("update:modelValue", outgoing);
  },
  { deep: true }
);

const descriptionLength = computed(() => localSeriesData.value.description?.length || 0);
const tooLong = computed(() => descriptionLength.value > MAX_TEXT);
const notesLength = computed(() => localSeriesData.value.notes?.length || 0);
const notesTooLong = computed(() => notesLength.value > MAX_TEXT);

onMounted(getSeriesFields);

async function getSeriesFields() {
  try {
    const responses = await Promise.all(seriesFields.map((field) => SeriesService.getSeriesFieldValues(field)));
    seriesFields.forEach((field, i) => {
      fieldValues.value[field] = responses[i].data;
    });
  } catch (error) {
    console.error("Could not load series field values:", error);
  }
}
</script>
