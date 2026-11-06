<template>
  <SettingsSection>
    <SettingsPanel as="form" title="3D shelf" description="Who stands on the shelf, how the issues line up, and which ones are out." @submit.prevent="save">
      <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-400">
        <i class="pi pi-spin pi-spinner"></i> Loading
      </div>

      <div v-else class="flex flex-col gap-7">
        <div class="flex flex-col gap-3">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <span class="text-sm font-medium text-slate-300">Standees</span>
              <p class="text-xs text-slate-500">Two framed characters in the shelf's end slots.</p>
            </div>
            <label class="flex items-center gap-2 text-sm text-slate-300">
              <ToggleSwitch v-model="choosing" inputId="standees-choose" />
              <span>Choose them</span>
            </label>
          </div>
          <p v-if="!choosing" class="text-sm text-slate-400">Automatic: the two characters you have in the most series.</p>
          <div v-else class="grid gap-4 sm:grid-cols-2">
            <div v-for="slot in [0, 1]" :key="slot" class="flex flex-col gap-1.5">
              <label :for="`standee-${slot}`" class="text-xs font-semibold uppercase tracking-wide text-slate-500">Slot {{ slot + 1 }}</label>
              <AutoComplete :inputId="`standee-${slot}`" v-model="standees[slot]" :suggestions="suggestions" optionLabel="title"
                dropdown forceSelection fluid placeholder="Search your characters" @complete="search">
                <template #option="{ option }">
                  <span class="flex items-center gap-3">
                    <img :src="imageOf(option)" alt="" class="h-9 w-7 rounded bg-slate-800 object-cover" />
                    <span class="min-w-0">
                      <span class="block truncate">{{ option.title }}</span>
                      <span class="block text-xs text-slate-500">in {{ option.series_count }} series</span>
                    </span>
                  </span>
                </template>
              </AutoComplete>
            </div>
          </div>
          <p v-if="choosing" class="text-xs text-slate-500">Only characters with a picture are offered. An empty slot stays empty.</p>
        </div>

        <div class="grid gap-5 sm:grid-cols-2">
          <div class="flex flex-col gap-1.5">
            <label for="shelf-order" class="text-sm font-medium text-slate-300">Order</label>
            <Select inputId="shelf-order" v-model="form.order" :options="orders" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label for="shelf-publisher" class="text-sm font-medium text-slate-300">Publisher</label>
            <Select inputId="shelf-publisher" v-model="form.publisher" :options="publishers" optionLabel="title" optionValue="id"
              filter showClear placeholder="Any publisher" class="w-full" />
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <span class="text-sm font-medium text-slate-300">Shelve</span>
          <SelectButton v-model="form.show" :options="shows" optionLabel="label" optionValue="value" :allowEmpty="false" />
          <p class="text-xs text-slate-500">Unread only turns the shelf into your to-read pile.</p>
        </div>
      </div>

      <template #footer>
        <Button v-if="dirty" type="button" label="Reset" size="small" text severity="secondary" :disabled="saving" @click="reset" />
        <Button type="submit" label="Save changes" size="small" :loading="saving" :disabled="loading || !dirty" />
      </template>
    </SettingsPanel>
  </SettingsSection>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import AutoComplete, { type AutoCompleteCompleteEvent } from "primevue/autocomplete";
import Button from "primevue/button";
import Select from "primevue/select";
import SelectButton from "primevue/selectbutton";
import ToggleSwitch from "primevue/toggleswitch";
import { useToast } from "primevue/usetoast";
import CharacterService from "@/services/CharacterService";
import PublisherService from "@/services/PublisherService";
import ShelfService from "@/services/ShelfService";
import type { Entity } from "@/types/entity.types";
import { SHELF_DEFAULTS, type ShelfSettings } from "@/types/shelf.types";
import SettingsSection from "@/components/settings/SettingsSection.vue";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const orders = [
  { value: "publisher", label: "Publisher, then series" },
  { value: "series", label: "Series, then number" },
  { value: "newest", label: "Newest pickups first" },
  { value: "unread", label: "Unread first" },
];
const shows = [
  { value: "all", label: "Every issue" },
  { value: "unread", label: "Unread only" },
];

const loading = ref(true);
const saving = ref(false);
const original = ref<ShelfSettings>({ ...SHELF_DEFAULTS });
const form = reactive<ShelfSettings>({ ...SHELF_DEFAULTS });
const choosing = ref(false);
const standees = ref<(Entity | null)[]>([null, null]);
const suggestions = ref<Entity[]>([]);
const publishers = ref<Entity[]>([]);

const chosenIds = computed(() => (choosing.value ? standees.value.filter((c): c is Entity => !!c).map((c) => c.id) : null));
const current = computed<ShelfSettings>(() => ({ standees: chosenIds.value, order: form.order, show: form.show, publisher: form.publisher }));
const dirty = computed(() => JSON.stringify(current.value) !== JSON.stringify(original.value));

const imageOf = (c: Entity) => CharacterService.getCharacterImageById(c.id, c.last_updated);

async function search(event: AutoCompleteCompleteEvent) {
  const page = await CharacterService.fetchCharacters(12, 0, event.query.trim());
  suggestions.value = ((page?.data ?? []) as Entity[]).filter((c) => c.thumbnail);
}

async function apply(settings: ShelfSettings) {
  original.value = { ...settings, standees: settings.standees ? [...settings.standees] : null };
  form.order = settings.order;
  form.show = settings.show;
  form.publisher = settings.publisher;
  choosing.value = settings.standees !== null;
  const found = await Promise.all((settings.standees ?? []).slice(0, 2).map((id) => CharacterService.getCharacterById(id).catch(() => null)));
  standees.value = [found[0] ?? null, found[1] ?? null];
}

function reset() {
  void apply(original.value);
}

async function save() {
  if (!dirty.value) return;
  saving.value = true;
  try {
    await apply(await ShelfService.saveSettings(current.value));
    toast.add({ severity: "success", summary: "Saved", detail: "The shelf will look this way next time you open it.", life: 3000 });
  } catch (error: any) {
    toast.add({ severity: "error", summary: "Couldn't save", detail: error.response?.data?.description ?? error.message, life: 5000 });
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  try {
    const [settings, page] = await Promise.all([ShelfService.getSettings(), PublisherService.fetchPublishers(200, 0)]);
    publishers.value = (page?.data ?? []) as Entity[];
    await apply(settings);
  } catch (error: any) {
    toast.add({ severity: "error", summary: "Couldn't load", detail: error.message, life: 5000 });
  } finally {
    loading.value = false;
  }
});
</script>
