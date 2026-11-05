<template>
  <SettingsPanel danger title="Delete all data">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <p class="max-w-prose text-sm leading-relaxed text-slate-400">
        Removes every series and issue you've added, plus all publishers, creators, characters and genres.
        Your account, password and photo stay. This can't be undone, so download a backup first.
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
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@/store/user";
import AuthenticationService from "@/services/AuthenticationService";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const userStore = useUserStore();

const user = computed(() => userStore.user ?? userStore.getUser());
const username = computed(() => user.value?.username || "");

const confirmingDelete = ref(false);
const deleteConfirmation = ref("");
const deleteInput = ref<any>(null);
const deleting = ref(false);

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
