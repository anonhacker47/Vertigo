<template>
  <SettingsPanel title="Export as a spreadsheet">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <p class="max-w-prose text-sm leading-relaxed text-slate-400">
        An .xlsx file with a Series sheet, an Issues sheet and a Stats sheet.
        Prices are in {{ currencyName(user?.preferred_currency) || user?.preferred_currency || 'your currency' }}.
      </p>
      <Button type="button" label="Download .xlsx" icon="pi pi-download" size="small" outlined class="shrink-0"
        :loading="exporting" @click="exportCollection" />
    </div>
  </SettingsPanel>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@/store/user";
import TransferService from "@/services/TransferService";
import { currencyName } from "@/utils/currencies";
import { saveBlob } from "@/utils/download";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const userStore = useUserStore();
const user = computed(() => userStore.user ?? userStore.getUser());

const exporting = ref(false);

async function exportCollection() {
  exporting.value = true;
  try {
    const blob = await TransferService.exportSpreadsheet();
    saveBlob(blob, "vertigo-collection.xlsx");
    toast.add({ severity: "success", summary: "Download started", detail: "vertigo-collection.xlsx", life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Export failed", detail: "The spreadsheet couldn't be generated. Try again.", life: 5000 });
  } finally {
    exporting.value = false;
  }
}
</script>
