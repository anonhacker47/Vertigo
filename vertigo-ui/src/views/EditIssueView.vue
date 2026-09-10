<template>
  <div class="w-full flex flex-col items-center justify-center m-4 mb-2">
    <h1 class="text-3xl font-bold">Edit Issue</h1>
    <p v-if="issue" class="text-slate-400 mt-1">
      {{ issue.series?.title }} {{ issueNumberLabel(issue.number) }}
    </p>
  </div>

  <form v-if="issue" @submit.prevent autocomplete="on"
    class="z-0 flex items-start justify-center flex-1 gap-6 md:gap-12 md:flex-row flex-col px-4 pb-8">

    <div class="w-[24rem] max-w-full flex flex-col gap-3">
      <div class="h-[38rem]">
        <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
      </div>
      <p class="text-xs text-center text-slate-400">{{ coverStatusText }}</p>
      <button v-if="canUseSeriesCover" type="button" @click="useSeriesCover" class="btn btn-outline btn-sm w-full">
        Use series cover
      </button>
    </div>

    <EditIssueForm v-model="form" :saving="saving" @save="saveIssue" @delete="confirmDelete" />
  </form>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import type { Issue, IssueEditFields } from "@/types/issue.types";
import IssueService from "@/services/IssueService";
import SeriesService from "@/services/SeriesService";
import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import EditIssueForm from "@/components/forms/EditIssueForm.vue";
import { useConfirmAction } from "@/composables/useConfirmAction";
import { issueNumberLabel } from "@/utils/issueTitle";

const route = useRoute();
const router = useRouter();
const toast = useToast();
const { confirmAction } = useConfirmAction();

const seriesId = Number(route.params.seriesId);
const issueNumber = Number(route.params.number);
const seriesSlug = String(route.params.slug ?? "");

const dummy = new URL("../assets/dummy.webp", import.meta.url).href;

const issue = ref<Issue | null>(null);
const saving = ref(false);
const imagesrc = ref(dummy);
const form = ref<IssueEditFields>(emptyForm());

// Cover change the user asked for; null = leave the cover as it is.
const coverChange = ref<File | string | "remove" | null>(null);
let previewObjectUrl: string | null = null;

function emptyForm(): IssueEditFields {
  return {
    title: "",
    number: null,
    cover_date: "",
    description: "",
    notes: "",
    is_owned: false,
    bought_date: "",
    bought_price: null,
    is_read: false,
    read_date: "",
    metron_id: null,
    metron_url: "",
  };
}

const toDateInput = (value: unknown) => (value ? String(value).substring(0, 10) : "");
const toIso = (value: string) => (value ? new Date(value).toISOString() : null);

function seriesCoverUrl(): string {
  const series = issue.value?.series;
  return series?.thumbnail ? SeriesService.getSeriesImageById(series.id, series.last_updated) : dummy;
}

function currentCoverUrl(data: Issue): string {
  return data.thumbnail ? IssueService.getIssueImageById(data.id, data.last_updated) : seriesCoverUrl();
}

async function getIssue() {
  try {
    const response = await IssueService.getIssue(seriesId, issueNumber);
    const data: Issue = response.data;
    issue.value = data;

    form.value = {
      title: data.title ?? "",
      number: data.number,
      cover_date: toDateInput(data.cover_date),
      description: data.description ?? "",
      notes: data.notes ?? "",
      is_owned: !!data.is_owned,
      bought_date: toDateInput(data.bought_date),
      bought_price: data.bought_price ?? null,
      is_read: !!data.is_read,
      read_date: toDateInput(data.read_date),
      metron_id: data.metron_id ?? null,
      metron_url: data.metron_url ?? "",
    };

    revokePreview();
    coverChange.value = null;
    imagesrc.value = currentCoverUrl(data);
  } catch (error) {
    console.error("Error fetching issue:", error);
    toast.add({ severity: "error", summary: "Load Failed", detail: errorMessage(error), life: 4000 });
  }
}

const canUseSeriesCover = computed(() => {
  if (coverChange.value === "remove") return false;
  return !!issue.value?.thumbnail || coverChange.value !== null;
});

const coverStatusText = computed(() => {
  const change = coverChange.value;
  if (change === "remove") return "The series cover will be used after saving.";
  if (change instanceof File) return `New cover: ${change.name} (uploaded when you save).`;
  if (typeof change === "string") return "New cover from URL (downloaded when you save).";
  return issue.value?.thumbnail ? "Showing this issue's own cover." : "Showing the series cover.";
});

function revokePreview() {
  if (previewObjectUrl) {
    URL.revokeObjectURL(previewObjectUrl);
    previewObjectUrl = null;
  }
}

function onImageChange(value: File | string) {
  // ImageUploader emits "noimage" when a preview fails to load and the dummy URL when its
  // link field is cleared; neither is a request to change the cover.
  if (value === "noimage") return;
  if (typeof value === "string" && (value === dummy || !value.trim())) {
    revokePreview();
    coverChange.value = null;
    imagesrc.value = issue.value ? currentCoverUrl(issue.value) : dummy;
    return;
  }

  revokePreview();
  coverChange.value = value;
  if (value instanceof File) {
    previewObjectUrl = URL.createObjectURL(value);
    imagesrc.value = previewObjectUrl;
  } else {
    imagesrc.value = value;
  }
}

function useSeriesCover() {
  revokePreview();
  coverChange.value = issue.value?.thumbnail ? "remove" : null;
  imagesrc.value = seriesCoverUrl();
}

function errorMessage(error: any): string {
  const data = error?.response?.data;
  if (typeof data?.error === "string") return data.error;

  // Marshmallow/APIFairy validation errors arrive as nested {field: [messages]} maps.
  const fieldErrors = data?.errors?.json ?? data?.errors ?? data?.messages?.json ?? data?.messages;
  if (fieldErrors && typeof fieldErrors === "object") {
    const [field, messages] = Object.entries(fieldErrors)[0] ?? [];
    if (field) return `${field}: ${([] as unknown[]).concat(messages as never).join(", ")}`;
  }

  if (typeof data?.message === "string") return data.message;
  return error?.message || String(error);
}

async function saveIssue() {
  if (!issue.value || saving.value) return;
  saving.value = true;

  const f = form.value;
  const payload = {
    title: f.title.trim(),
    number: f.number,
    cover_date: toIso(f.cover_date),
    description: f.description?.trim() || null,
    notes: f.notes?.trim() || null,
    is_owned: f.is_owned,
    is_read: f.is_read,
    bought_date: f.is_owned ? toIso(f.bought_date) : null,
    bought_price: f.is_owned ? (f.bought_price ?? null) : null,
    read_date: f.is_read ? toIso(f.read_date) : null,
    metron_id: f.metron_id || null,
    metron_url: f.metron_url?.trim() || null,
  };

  try {
    const response = await IssueService.updateIssue(issue.value.id, payload);
    const updated: Issue = response.data;

    // Cover changes go through their own endpoint; a failure there shouldn't undo the saved fields.
    try {
      if (coverChange.value === "remove") {
        await IssueService.removeIssueCover(issue.value.id);
      } else if (coverChange.value) {
        await IssueService.updateIssueCover(issue.value.id, coverChange.value);
      }
    } catch (coverError) {
      toast.add({ severity: "warn", summary: "Cover Not Updated", detail: errorMessage(coverError), life: 5000 });
    }

    toast.add({ severity: "success", summary: "Issue Updated", detail: `${updated.title} saved.`, life: 2500 });
    router.push({
      name: "IssueDetail",
      params: { seriesId: String(seriesId), slug: seriesSlug, number: String(updated.number ?? f.number) },
    });
  } catch (error) {
    toast.add({ severity: "error", summary: "Update Failed", detail: errorMessage(error), life: 4000 });
  } finally {
    saving.value = false;
  }
}

function confirmDelete() {
  if (!issue.value) return;
  const target = issue.value;
  confirmAction({
    message: `Issue ${target.title}`,
    header: "Confirm Deletion",
    acceptLabel: "Delete",
    severity: "danger",
    successMessage: `${target.title} deleted`,
    onAccept: () => deleteIssue(target),
  });
}

async function deleteIssue(target: Issue) {
  try {
    await IssueService.removeIssue(target.id);
    toast.add({ severity: "success", summary: "Issue Deleted", detail: `${target.title} deleted.`, life: 2500 });
    router.push({ name: "SeriesDetail", params: { Id: String(seriesId), Link: seriesSlug } });
  } catch (error) {
    toast.add({ severity: "error", summary: "Delete Failed", detail: errorMessage(error), life: 4000 });
  }
}

onMounted(getIssue);
onBeforeUnmount(revokePreview);
</script>
