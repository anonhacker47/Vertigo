<template>
  <SettingsPanel title="Restore a backup">
    <div class="flex flex-col gap-4">
      <p class="max-w-prose text-sm leading-relaxed text-slate-400">
        Bring back a backup .zip from above. Into an empty collection it restores everything as it was,
        covers included. If you already have series here you'll be asked whether to merge or replace.
      </p>

      <TransferProgress v-if="run" :run="run" :percent="percent" :result="result" busy-title="Restoring"
        :dismiss-label="run.status === 'done' ? 'Done' : 'Dismiss'" @dismiss="finish">
        <p v-if="run.status === 'failed' && landed" class="mt-1 text-xs leading-relaxed text-slate-400">
          {{ landed }} Run the restore again and choose Merge to add what is still missing.
        </p>
        <p v-if="run.status === 'done' && safetyCopy" class="mt-1 text-xs leading-relaxed text-slate-500">
          The collection it replaced was saved on the server as {{ safetyCopy }}, in the data folder's backups directory.
        </p>
      </TransferProgress>

      <template v-else>
        <FilePicker v-model="file" accept=".zip,application/zip" label="Choose a backup"
          hint="A vertigo-backup-….zip" :disabled="submitting" @update:model-value="conflict = null" />

        <div v-if="conflict" class="conflict">
          <p class="text-sm text-slate-200">
            Your collection already has
            <strong class="text-slate-100">{{ count(conflict.account.series, 'series', 'series') }}</strong>
            and <strong class="text-slate-100">{{ count(conflict.account.issues, 'issue') }}</strong>.
            The backup holds {{ count(conflict.backup.series, 'series', 'series') }} and
            {{ count(conflict.backup.issues, 'issue') }}<template v-if="backupOrigin">, {{ backupOrigin }}</template>.
          </p>

          <div class="mt-4 grid gap-3 sm:grid-cols-2" role="radiogroup" aria-label="How to restore">
            <label v-for="option in modes" :key="option.value" class="mode" :class="{ 'mode--on': mode === option.value, 'mode--danger': option.value === 'replace' }">
              <input v-model="mode" type="radio" name="restore-mode" :value="option.value" class="sr-only" />
              <span class="mode__title">{{ option.title }}</span>
              <span class="mode__text">{{ option.text }}</span>
            </label>
          </div>

          <div v-if="mode === 'replace' && confirmingReplace" class="mt-4 flex flex-wrap items-center gap-2 text-sm text-red-200">
            <span class="mr-auto">Delete your {{ count(conflict.account.series, 'series', 'series') }} first? This can't be undone.</span>
            <Button type="button" label="Cancel" size="small" text severity="secondary" @click="confirmingReplace = false" />
            <Button type="button" label="Delete and restore" size="small" severity="danger" :loading="submitting" @click="submit('replace')" />
          </div>
          <div v-else class="mt-4 flex flex-wrap items-center justify-end gap-2">
            <Button type="button" label="Cancel" size="small" text severity="secondary" :disabled="submitting" @click="cancelConflict" />
            <Button v-if="mode === 'replace'" type="button" label="Replace collection" icon="pi pi-trash" size="small"
              severity="danger" outlined :disabled="submitting" @click="confirmingReplace = true" />
            <Button v-else type="button" label="Merge backup" icon="pi pi-plus" size="small"
              :loading="submitting" @click="submit('merge')" />
          </div>
        </div>

        <div v-else class="flex justify-end">
          <Button type="button" label="Restore" icon="pi pi-history" size="small" :disabled="!file"
            :loading="submitting" @click="submit()" />
        </div>
      </template>
    </div>
  </SettingsPanel>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import TransferService, { transferErrorMessage } from "@/services/TransferService";
import { useTransferRun } from "@/composables/useTransferRun";
import type { RestoreConflict, RestoreMode } from "@/types/transfer.types";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";
import TransferProgress from "@/components/settings/TransferProgress.vue";
import FilePicker from "@/components/common/FilePicker.vue";

const toast = useToast();
const { run, percent, track, reset } = useTransferRun();

const file = ref<File | null>(null);
const submitting = ref(false);
const conflict = ref<RestoreConflict | null>(null);
const mode = ref<RestoreMode>("merge");
const confirmingReplace = ref(false);
const usedMode = ref<RestoreMode | null>(null);

const modes: { value: RestoreMode; title: string; text: string }[] = [
  { value: "merge", title: "Merge", text: "Adds what you don't have. Nothing you already have is changed." },
  { value: "replace", title: "Replace", text: "Deletes everything in your collection first, then restores the backup." },
];

function count(n: number, singular: string, plural = `${singular}s`) {
  return `${n.toLocaleString()} ${n === 1 ? singular : plural}`;
}

const backupOrigin = computed(() => {
  const info = conflict.value?.backup;
  if (!info) return "";
  const parts: string[] = [];
  if (info.username) parts.push(`from ${info.username}`);
  if (info.created_at) {
    const date = new Date(info.created_at);
    if (!Number.isNaN(date.getTime())) parts.push(`made ${date.toLocaleDateString(undefined, { dateStyle: "medium" })}`);
  }
  return parts.join(" ");
});

function number(value: number | string | undefined): number {
  return typeof value === "number" ? value : 0;
}

const safetyCopy = computed(() => {
  const value = run.value?.summary?.safety_backup;
  return typeof value === "string" ? value : "";
});

const result = computed(() => {
  const s = run.value?.summary ?? {};
  if (usedMode.value === "merge") {
    const skipped = number(s.issues_skipped) ? ` ${count(number(s.issues_skipped), "issue")} were already here.` : "";
    return `Added ${count(number(s.series), "series", "series")} and ${count(number(s.issues), "issue")}.${skipped}`;
  }
  const images = number(s.images) ? ` and ${count(number(s.images), "image")}` : "";
  return `Restored ${count(number(s.series), "series", "series")}, ${count(number(s.issues), "issue")}${images}.`;
});

/** What a failed run managed before stopping, or "" when nothing did. */
const landed = computed(() => {
  const s = run.value?.summary ?? {};
  const series = number(s.series);
  const issues = number(s.issues);
  if (!series && !issues) return "";
  return `${count(series, "series", "series")} and ${count(issues, "issue")} were restored before it stopped.`;
});

function cancelConflict() {
  conflict.value = null;
  confirmingReplace.value = false;
  mode.value = "merge";
}

async function submit(chosen?: RestoreMode) {
  if (!file.value || submitting.value) return;
  submitting.value = true;
  try {
    const started = await TransferService.restore(file.value, chosen);
    usedMode.value = chosen ?? null;
    track(started);
    file.value = null;
    cancelConflict();
  } catch (error) {
    const body = (error as { response?: { status?: number; data?: RestoreConflict } })?.response;
    if (body?.status === 409 && body.data?.error === "account_not_empty") {
      conflict.value = body.data;
    } else {
      toast.add({
        severity: "error",
        summary: "Couldn't restore",
        detail: transferErrorMessage(error, "The file couldn't be read. Try again."),
        life: 6000,
      });
    }
  } finally {
    submitting.value = false;
  }
}

function finish() {
  reset();
  usedMode.value = null;
}
</script>

<style scoped>
.conflict {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(251, 191, 36, 0.25);
  background: rgba(251, 191, 36, 0.05);
}
.mode {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(2, 6, 23, 0.35);
  cursor: pointer;
  transition: border-color 0.12s ease, background-color 0.12s ease;
}
.mode:hover {
  border-color: rgba(148, 163, 184, 0.4);
}
.mode:focus-within {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}
.mode--on {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.08);
}
.mode--danger.mode--on {
  border-color: #f87171;
  background: rgba(248, 113, 113, 0.08);
}
.mode__title {
  font-size: 14px;
  font-weight: 700;
  color: #f1f5f9;
}
.mode__text {
  font-size: 12.5px;
  line-height: 1.45;
  color: #94a3b8;
}
</style>
