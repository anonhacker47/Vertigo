<template>
  <SettingsSection title="Your data"
    description="Everything you've catalogued: series, issues, publishers, creators, characters and genres.">
    <SettingsPanel title="Export as a spreadsheet">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <p class="max-w-prose text-sm leading-relaxed text-slate-400">
          An .xlsx file with a Series sheet, an Issues sheet and a Stats sheet.
          Prices are in {{ currencyName(user?.preferred_currency) || user?.preferred_currency || 'your currency' }}.
        </p>
        <Button type="button" label="Download .xlsx" icon="pi pi-download" size="small" outlined
          class="shrink-0" :loading="exporting" @click="exportCollection" />
      </div>
    </SettingsPanel>

    <SettingsPanel danger title="Delete all data">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <p class="max-w-prose text-sm leading-relaxed text-slate-400">
          Removes every series and issue you've added, plus all publishers, creators, characters and genres.
          Your account, password and photo stay. This can't be undone.
        </p>
        <Button v-if="!confirmingDelete" type="button" label="Delete all data" icon="pi pi-trash" size="small"
          severity="danger" outlined class="shrink-0" @click="startDelete" />
      </div>

      <form v-if="confirmingDelete" class="mt-5 flex flex-col gap-3 border-t border-red-900/40 pt-5"
        @submit.prevent="deleteAllData">
        <label for="confirm-delete" class="text-sm text-slate-300">
          Type <span class="font-semibold text-slate-100">{{ username }}</span> to confirm
        </label>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <InputText id="confirm-delete" ref="deleteInput" v-model="deleteConfirmation" autocomplete="off"
            class="w-full sm:w-72" />
          <Button type="submit" label="Delete everything" size="small" severity="danger"
            :disabled="!username || deleteConfirmation !== username" :loading="deleting" />
          <Button type="button" label="Cancel" size="small" text severity="secondary" @click="cancelDelete" />
        </div>
      </form>
    </SettingsPanel>
  </SettingsSection>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@/store/user";
import AuthenticationService from "@/services/AuthenticationService";
import { currencyName } from "@/utils/currencies";
import SettingsSection from "@/components/settings/SettingsSection.vue";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const userStore = useUserStore();

const user = computed(() => userStore.user ?? userStore.getUser());
const username = computed(() => user.value?.username || "");

const exporting = ref(false);
const confirmingDelete = ref(false);
const deleteConfirmation = ref("");
const deleteInput = ref<any>(null);
const deleting = ref(false);

async function exportCollection() {
  exporting.value = true;
  try {
    const data = await AuthenticationService.exportCollection();
    const url = window.URL.createObjectURL(new Blob([data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "vertigo-collection.xlsx");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    toast.add({ severity: "success", summary: "Download started", detail: "vertigo-collection.xlsx", life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Export failed", detail: "The spreadsheet couldn't be generated. Try again.", life: 5000 });
  } finally {
    exporting.value = false;
  }
}

async function startDelete() {
  confirmingDelete.value = true;
  deleteConfirmation.value = "";
  await nextTick();
  deleteInput.value?.$el?.focus?.();
}

function cancelDelete() {
  confirmingDelete.value = false;
  deleteConfirmation.value = "";
}

async function deleteAllData() {
  if (!username.value || deleteConfirmation.value !== username.value) return;

  deleting.value = true;
  try {
    const response = await AuthenticationService.deleteAllData();
    const seriesGone = response.data?.deleted?.series ?? 0;
    cancelDelete();
    toast.add({
      severity: "success",
      summary: "Deleted",
      detail: `${seriesGone} series and their issues are gone.`,
      life: 4000,
    });
  } catch {
    toast.add({ severity: "error", summary: "Couldn't delete", detail: "Nothing was removed. Try again.", life: 5000 });
  } finally {
    deleting.value = false;
  }
}
</script>
