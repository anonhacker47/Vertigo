<template>
  <SettingsPanel title="Back up everything">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <p class="max-w-prose text-sm leading-relaxed text-slate-400">
        A .zip with every series, issue, publisher, creator, character and genre, your ratings, dates,
        prices and notes, your 3D shelf setup, and all your covers. Restore it below, here or on another Vertigo server.
      </p>
      <Button type="button" label="Download backup" icon="pi pi-download" size="small" outlined class="shrink-0"
        :loading="downloading" @click="download" />
    </div>
  </SettingsPanel>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@/store/user";
import TransferService from "@/services/TransferService";
import { dateStamp, saveBlob } from "@/utils/download";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const userStore = useUserStore();
const user = computed(() => userStore.user ?? userStore.getUser());

const downloading = ref(false);

async function download() {
  downloading.value = true;
  const filename = `vertigo-backup-${user.value?.username || "collection"}-${dateStamp()}.zip`;
  try {
    const blob = await TransferService.downloadBackup();
    saveBlob(blob, filename);
    toast.add({ severity: "success", summary: "Download started", detail: filename, life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Backup failed", detail: "The backup couldn't be built. Try again.", life: 5000 });
  } finally {
    downloading.value = false;
  }
}
</script>
