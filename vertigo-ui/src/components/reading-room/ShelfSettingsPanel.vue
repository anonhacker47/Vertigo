<template>
  <Transition name="glass">
    <form v-if="visible" class="glass" aria-label="Shelf settings" @submit.prevent="save">
      <header class="glass__head">
        <h2>Shelf settings</h2>
        <button type="button" class="glass__close" aria-label="Close" @click="$emit('update:visible', false)"><i class="pi pi-times"></i></button>
      </header>
      <div class="flex flex-col gap-7">
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

        <div class="flex flex-col gap-1.5">
          <span class="text-sm font-medium text-slate-300">Bookcase</span>
          <SelectButton v-model="form.finish" :options="finishes" optionLabel="label" optionValue="value" :allowEmpty="false" />
          <p class="text-xs text-slate-500">White is the plain flat-pack look.</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-end gap-2">
        <Button v-if="dirty" type="button" label="Reset" size="small" text severity="secondary" @click="reset" />
        <Button type="submit" label="Save changes" size="small" :disabled="!dirty" />
      </div>
    </form>
  </Transition>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
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

const props = defineProps<{ visible: boolean; settings: ShelfSettings }>();
const emit = defineEmits<{ "update:visible": [open: boolean]; saved: [settings: ShelfSettings] }>();

const toast = useToast();
const orders = [
  { value: "publisher", label: "Publisher, then series" },
  { value: "series", label: "Series, then number" },
  { value: "newest", label: "Newest pickups first" },
  { value: "unread", label: "Unread first" },
];
const shows = [
  { value: "all", label: "Owned issues" },
  { value: "unread", label: "Unread only" },
];

const finishes = [
  { value: "charcoal", label: "Charcoal" },
  { value: "white", label: "White" },
];

const original = ref<ShelfSettings>({ ...SHELF_DEFAULTS });
const form = reactive<ShelfSettings>({ ...SHELF_DEFAULTS });
const choosing = ref(false);
const standees = ref<(Entity | null)[]>([null, null]);
const suggestions = ref<Entity[]>([]);
const publishers = ref<Entity[]>([]);

const chosenIds = computed(() => (choosing.value ? [...new Set(standees.value.filter((c): c is Entity => !!c).map((c) => c.id))] : null));
const current = computed<ShelfSettings>(() => ({ standees: chosenIds.value, order: form.order, show: form.show, publisher: form.publisher, finish: form.finish }));
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
  form.finish = settings.finish;
  choosing.value = settings.standees !== null;
  const found = await Promise.all((settings.standees ?? []).slice(0, 2).map((id) => CharacterService.getCharacterById(id).catch(() => null)));
  standees.value = [found[0] ?? null, found[1] ?? null];
}

function reset() {
  void apply(original.value);
}

// the shelf changes at once; the save follows behind it
function save() {
  if (!dirty.value) return;
  const before = original.value, next = current.value;
  emit("saved", next);
  emit("update:visible", false);
  ShelfService.saveSettings(next).catch((error: any) => {
    emit("saved", before);
    toast.add({ severity: "error", summary: "Couldn't save", detail: error.response?.data?.description ?? error.message, life: 5000 });
  });
}

watch(() => props.visible, (open) => {
  if (!open) return;
  void apply(props.settings);
  if (publishers.value.length) return;
  PublisherService.fetchPublishers(200, 0)
    .then((page) => { publishers.value = (page?.data ?? []) as Entity[]; })
    .catch((error: any) => toast.add({ severity: "error", summary: "Couldn't load publishers", detail: error.message, life: 5000 }));
}, { immediate: true });
</script>

<style scoped>
/* frosted glass, like the cards the room shows for a picked-up comic */
.glass {
  position: absolute; left: 50%; top: 50%; z-index: 5;
  display: flex; flex-direction: column; gap: 24px;
  width: min(560px, calc(100% - 32px));
  max-height: calc(100% - 32px);
  overflow-y: auto;
  padding: 22px 24px 24px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(12, 14, 22, 0.5);
  -webkit-backdrop-filter: blur(22px) saturate(1.3);
  backdrop-filter: blur(22px) saturate(1.3);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transform: translate(-50%, -50%);
}
.glass__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.glass__head h2 { margin: 0; font-size: 22px; font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; color: #fff; }
.glass__close { display: grid; place-items: center; width: 32px; height: 32px; border-radius: 999px; color: #94a3b8; font-size: 13px; }
.glass__close:hover { color: #fff; background: rgba(255, 255, 255, 0.1); }
.glass-enter-active { transition: opacity 0.3s, transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1); }
.glass-leave-active { transition: opacity 0.2s; }
.glass-enter-from { opacity: 0; transform: translate(-50%, calc(-50% + 20px)); }
.glass-leave-to { opacity: 0; }
@media (prefers-reduced-motion: reduce) {
  .glass-enter-active, .glass-leave-active { transition: none; }
}
</style>
