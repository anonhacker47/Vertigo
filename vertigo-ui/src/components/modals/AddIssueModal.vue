<template>
  <Dialog
    :visible="visible"
    modal
    header="Add an issue"
    class="w-[95vw] md:w-176"
    :draggable="false"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="grid gap-6 sm:grid-cols-[10rem_minmax(0,1fr)]">
      <div class="mx-auto w-40 sm:mx-0 sm:w-auto">
        <ImageUploader v-model="coverPreview" :title="coverTitle" @image-change="onCoverChange" />
      </div>

      <div class="grid content-start gap-4 sm:grid-cols-[9rem_minmax(0,1fr)]">
        <div>
          <label for="new-issue-number" class="fm-label">Number</label>
          <InputNumber
            v-model="form.number"
            input-id="new-issue-number"
            :min="0"
            :use-grouping="false"
            fluid
            :invalid="!!numberError"
            :aria-describedby="numberError ? 'new-issue-number-error' : undefined"
          />
        </div>
        <div>
          <label for="new-issue-title" class="fm-label">Title</label>
          <input
            id="new-issue-title"
            v-model="form.title"
            type="text"
            maxlength="280"
            class="fm-input"
            :placeholder="numberLabel ? `Issue ${numberLabel}` : 'Issue title'"
            autocomplete="off"
          />
        </div>
        <Message v-if="numberError" id="new-issue-number-error" severity="error" size="small" variant="simple" class="-mt-2 sm:col-span-2">{{ numberError }}</Message>

        <div class="flex flex-wrap items-center gap-2 sm:col-span-2">
          <button type="button" class="fm-toggle fm-toggle--own" :aria-pressed="form.is_owned" @click="form.is_owned = !form.is_owned">Own</button>
          <button type="button" class="fm-toggle fm-toggle--read" :aria-pressed="form.is_read" @click="form.is_read = !form.is_read">Read</button>
          <p class="fm-hint basis-full">Marking it owned or read stamps today's date; change it below.</p>
        </div>

        <template v-if="form.is_owned">
          <div>
            <label for="new-issue-bought" class="fm-label">Bought on</label>
            <DatePicker :model-value="ymdToDate(form.bought_date)" input-id="new-issue-bought" date-format="d M yy" show-icon icon-display="input" fluid
              @update:model-value="form.bought_date = dateToYmd($event as Date | null)" />
          </div>
          <div>
            <label for="new-issue-price" class="fm-label">Price</label>
            <InputNumber v-model="form.bought_price" input-id="new-issue-price" mode="decimal" :min="0" :max-fraction-digits="2" placeholder="0.00" fluid />
          </div>
        </template>
        <div v-if="form.is_read" class="sm:col-span-2">
          <label for="new-issue-read" class="fm-label">Read on</label>
          <DatePicker :model-value="ymdToDate(form.read_date)" input-id="new-issue-read" date-format="d M yy" show-icon icon-display="input" class="w-full sm:w-44"
            @update:model-value="form.read_date = dateToYmd($event as Date | null)" />
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" severity="secondary" outlined :disabled="saving" @click="close" />
      <Button :label="saving ? 'Adding' : 'Add issue'" :loading="saving" :disabled="!!numberError" @click="submit" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import DatePicker from "primevue/datepicker";
import InputNumber from "primevue/inputnumber";
import Message from "primevue/message";
import { dateToYmd, todayYmd, ymdToDate } from "@/utils/dateInput";
import { useToast } from "primevue/usetoast";
import IssueService from "@/services/IssueService";
import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import type { Issue, NewIssue } from "@/types/issue.types";

const props = defineProps<{
  visible: boolean;
  seriesId: number;
  takenNumbers: number[];
  defaultNumber: number;
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "added", issue: Issue): void;
}>();

const toast = useToast();
const dummy = new URL("../../assets/dummy.webp", import.meta.url).href;

const blank = () => ({
  number: props.defaultNumber as number | null,
  title: "",
  is_owned: false,
  is_read: false,
  bought_date: todayYmd() as string | null,
  read_date: todayYmd() as string | null,
  bought_price: null as number | null,
});

const form = ref(blank());
const cover = ref<File | string | null>(null);
const coverPreview = ref(dummy);
const saving = ref(false);

watch(() => props.visible, (open) => {
  if (!open) return;
  form.value = blank();
  cover.value = null;
  coverPreview.value = dummy;
});

const numberLabel = computed(() => (form.value.number == null ? "" : String(form.value.number)));
const coverTitle = computed(() => form.value.title.trim() || (numberLabel.value ? `#${numberLabel.value}` : ""));

const numberError = computed(() => {
  const n = form.value.number;
  if (n === null || n === undefined || Number.isNaN(n)) return "Give the issue a number.";
  if (!Number.isInteger(n) || n < 0) return "Use a whole number, 0 or more.";
  if (props.takenNumbers.includes(n)) return `Issue #${n} already exists in this series.`;
  return "";
});

function onCoverChange(value: File | string) {
  if (value instanceof File) cover.value = value;
  else if (!value || value === "noimage" || value === dummy) cover.value = null;
  else cover.value = value.trim() || null;
}

function close() {
  emit("update:visible", false);
}

async function submit() {
  if (saving.value || numberError.value) return;
  saving.value = true;

  try {
    const payload: NewIssue = {
      number: form.value.number as number,
      is_owned: form.value.is_owned,
      is_read: form.value.is_read,
    };
    const title = form.value.title.trim();
    if (title) payload.title = title;
    if (form.value.is_owned) {
      payload.bought_date = ymdToDate(form.value.bought_date)?.toISOString() ?? null;
      payload.bought_price = form.value.bought_price ?? null;
    }
    if (form.value.is_read) {
      payload.read_date = ymdToDate(form.value.read_date)?.toISOString() ?? null;
    }

    const { data: issue } = await IssueService.createIssue(props.seriesId, payload);

    if (cover.value) {
      try {
        await IssueService.updateIssueCover(issue.id, cover.value);
      } catch (error) {
        console.error("Issue cover upload failed:", error);
        toast.add({ severity: "warn", summary: "Cover not saved", detail: "The issue was added, but its cover could not be saved. Set it from the issue page.", life: 5000 });
      }
    }

    emit("added", issue);
    close();
  } catch (error: any) {
    const data = error?.response?.data;
    toast.add({
      severity: "error",
      summary: "Could not add issue",
      detail: data?.description || data?.message || error?.message || "Unexpected error.",
      life: 4000,
    });
  } finally {
    saving.value = false;
  }
}
</script>
