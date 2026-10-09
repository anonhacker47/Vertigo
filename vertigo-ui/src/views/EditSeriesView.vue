<template>
  <div class="mx-auto w-full max-w-page px-4 pt-6 md:px-8">
    <header>
      <h1 class="text-3xl font-extrabold tracking-tight text-white">Edit series</h1>
      <p class="mt-1 text-sm font-semibold text-slate-400">{{ loaded ? seriesData.title || "Untitled series" : "Loading the series" }}</p>
    </header>

    <form
      id="series-form"
      class="mt-7 grid gap-8 md:grid-cols-[14rem_minmax(0,1fr)] md:gap-10 xl:grid-cols-[16rem_minmax(0,1fr)]"
      autocomplete="on"
      novalidate
      @submit.prevent
    >
      <aside class="mx-auto w-56 max-w-full md:sticky md:top-[calc(var(--spacing-header)+1.5rem)] md:mx-0 md:w-auto md:self-start">
        <ImageUploader v-model="imagesrc" :title="seriesData.title" @image-change="onImageChange" />
      </aside>

      <div class="min-w-0" :class="{ 'opacity-50': !loaded }">
        <SeriesDetailsForm v-model="seriesData" :errors="errors" metron-editable />
      </div>
    </form>
  </div>

  <div class="fm-actionbar">
    <div class="mx-auto flex w-full max-w-page items-center justify-between gap-4 px-4 md:px-8">
      <Button label="Delete series" icon="pi pi-trash" severity="danger" outlined :disabled="!loaded || saving" @click="confirmDelete" />
      <div class="flex shrink-0 items-center gap-3">
        <Button label="Cancel" severity="secondary" outlined :disabled="saving" @click="router.back()" />
        <Button :label="saving ? 'Saving' : 'Save details'" :loading="saving" :disabled="!loaded" @click="updateSeries" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";

import type { SeriesFormData } from "@/types/series.types";

import SeriesService from "../services/SeriesService";
import { useConfirmAction } from "@/composables/useConfirmAction";

import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import SeriesDetailsForm, { type SeriesFormErrors } from "@/components/forms/SeriesDetailsForm.vue";

const router = useRouter();
const route = useRoute();
const toast = useToast();
const { confirmAction } = useConfirmAction();

const seriesId = Number(route.params.Id);
const imagesrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);
const loaded = ref(false);
const saving = ref(false);
const errors = ref<SeriesFormErrors>({});

const seriesData = ref<SeriesFormData>({
  title: "",
  creator: [],
  description: "",
  notes: "",
  genre: [],
  character: [],
  series_format: "",
  issue_count: 1,
  thumbnail: "",
  publisher: null,
  read_count: 0,
  owned_count: 0,
  metron_id: null,
  metron_url: null,
});

async function getSeries() {
  try {
    const response = await SeriesService.getSeriesbyId(seriesId);

    seriesData.value = {
      ...response,
      notes: response.notes || "",
      character: normalizeEntityArray(response.character),
      creator: normalizeEntityArray(response.creator),
      genre: normalizeEntityArray(
        (response.genre || []).map((g: any) => ({ id: g, title: g })),
        "title"
      ),
      publisher: normalizeSingleEntity(response.publisher),
    };

    imagesrc.value = `${SeriesService.getSeriesImageById(seriesId)}`;
    loaded.value = true;
  } catch (error) {
    console.error("Could not load series:", error);
    toast.add({ severity: "error", summary: "Could not load series", detail: "Try opening it again from the collection.", life: 4000 });
  }
}

// Clear a field's error as soon as it is fixed.
watch(() => seriesData.value.title, (title) => {
  if (errors.value.title && title?.trim()) errors.value = { ...errors.value, title: undefined };
});
watch(() => seriesData.value.series_format, (format) => {
  if (errors.value.series_format && format) errors.value = { ...errors.value, series_format: undefined };
});

function validate(): boolean {
  const next: SeriesFormErrors = {};
  if (!seriesData.value.title?.trim()) next.title = "Give the series a title.";
  if (!seriesData.value.series_format) next.series_format = "Choose a format.";
  errors.value = next;

  const firstInvalid = next.title ? "series-title" : next.series_format ? "series-format" : null;
  if (!firstInvalid) return true;

  const el = document.getElementById(firstInvalid);
  el?.scrollIntoView({ block: "center", behavior: "smooth" });
  el?.focus({ preventScroll: true });
  toast.add({ severity: "warn", summary: "Missing details", detail: "Add a title and choose a format.", life: 3000 });
  return false;
}

async function updateSeries() {
  if (saving.value || !validate()) return;
  saving.value = true;

  try {
    const formData = new FormData();
    const data = seriesData.value;

    formData.append("title", (data.title || "").trim());
    formData.append("description", data.description || "");
    formData.append("notes", data.notes || "");
    formData.append("series_format", data.series_format || "");
    formData.append("issue_count", String(data.issue_count || 0));
    formData.append("read_count", String(data.read_count || 0));
    formData.append("owned_count", String(data.owned_count || 0));
    // Empty means "no Metron link"; the backend treats "" as null.
    formData.append("metron_id", data.metron_id ? String(data.metron_id) : "");
    formData.append("metron_url", data.metron_url?.trim() || "");
    formData.append("character", JSON.stringify(data.character || []));
    formData.append("genre", JSON.stringify(data.genre || []));
    formData.append("creator", JSON.stringify(data.creator || []));
    const pub = data.publisher;
    formData.append("publisher", JSON.stringify(pub && typeof pub === "object" && pub.value ? [pub] : []));

    if (data.thumbnail) {
      formData.append("thumbnail", data.thumbnail);
    }

    const response = await SeriesService.updateSeries(seriesId, formData);
    toast.add({ severity: "success", summary: "Details saved", detail: `${data.title} is up to date.`, life: 3000 });
    router.push({
      name: "SeriesDetail",
      params: { Id: String(response.data.id), Link: response.data.link },
      query: { refresh: Date.now() },
    });
  } catch (error: any) {
    console.error("Update error:", error);
    toast.add({ severity: "error", summary: "Could not save", detail: error?.message || "Unexpected error.", life: 4000 });
  } finally {
    saving.value = false;
  }
}

function confirmDelete() {
  const title = seriesData.value.title || "this series";
  confirmAction({
    message: `Delete ${title} and all of its issues? This cannot be undone.`,
    header: "Delete series",
    acceptLabel: "Delete",
    severity: "danger",
    onAccept: deleteSeries,
  });
}

async function deleteSeries() {
  try {
    await SeriesService.removeSeries(seriesId);
    toast.add({ severity: "success", summary: "Series deleted", detail: `${seriesData.value.title} was removed from the shelf.`, life: 3000 });
    router.push({ name: "Collection" });
  } catch (error: any) {
    console.error("Delete error:", error);
    toast.add({ severity: "error", summary: "Could not delete", detail: error?.message || "Unexpected error.", life: 4000 });
  }
}

onMounted(getSeries);

function onImageChange(file: File | string) {
  seriesData.value.thumbnail = file;
  if (file instanceof File) {
    imagesrc.value = URL.createObjectURL(file);
  } else if (typeof file === "string") {
    imagesrc.value = file;
  }
}

function normalizeEntityArray(arr: any[], labelKey = "title") {
  if (!Array.isArray(arr)) return [];
  return arr.map((item) => ({
    id: item.id ?? item,
    value: typeof item === "string" ? item : item[labelKey],
  }));
}

function normalizeSingleEntity(item: any, labelKey = "title") {
  if (!item) return null;
  return { id: item.id, value: item[labelKey] };
}
</script>
