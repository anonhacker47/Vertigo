<template>
  <div class="relative w-full">
    <input
      :id="inputId"
      ref="inputEl"
      :value="open ? query : selectedLabel"
      type="text"
      class="fm-input pr-10"
      :placeholder="selectedLabel || placeholder"
      role="combobox"
      :aria-expanded="open"
      :aria-controls="listId"
      :aria-activedescendant="activeId"
      aria-autocomplete="list"
      autocomplete="off"
      @focus="onFocus"
      @input="onInput"
      @blur="onBlur"
      @keydown="onKeydown"
    />
    <!-- Wrapper carries the positioning: PrimeVue's button rule sets position on the button itself. -->
    <span v-if="localSelected && !open" class="absolute right-1 top-1/2 -translate-y-1/2">
      <Button
        icon="pi pi-times"
        text
        rounded
        size="small"
        severity="secondary"
        :aria-label="`Clear ${placeholder || 'selection'}`"
        @mousedown.prevent
        @click="selectItem(null)"
      />
    </span>
    <i v-else class="pi pi-chevron-down pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500" style="font-size: 11px"></i>

    <ul v-if="open && total" :id="listId" role="listbox" class="fm-menu">
      <li
        v-for="(item, i) in filteredItems"
        :id="optionId(i)"
        :key="keyOf(item)"
        role="option"
        :aria-selected="isSelected(item)"
        class="fm-menu__item"
        :class="{ 'is-active': i === active, 'is-checked': isSelected(item) }"
        @mousedown.prevent="selectItem(item)"
        @mousemove="active = i"
      >
        <span class="fm-menu__check"><i v-if="isSelected(item)" class="pi pi-check" style="font-size: 10px"></i></span>
        <span class="truncate">{{ item.value }}</span>
      </li>
      <li
        v-if="canCreate"
        :id="optionId(filteredItems.length)"
        role="option"
        :aria-selected="false"
        class="fm-menu__item fm-menu__item--create"
        :class="{ 'is-active': active === filteredItems.length }"
        @mousedown.prevent="addCustom"
        @mousemove="active = filteredItems.length"
      >
        <span class="fm-menu__check"><i class="pi pi-plus" style="font-size: 10px"></i></span>
        <span class="truncate">Add "{{ query.trim() }}"</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import Button from "primevue/button";

type Item = { id: any; value: string; title?: string; name?: string };

let uid = 0;
const MAX_SHOWN = 100;

const props = defineProps<{
  field?: string;
  placeholder?: string;
  items: Item[];
  modelValue: Item | null;
  /** id for the text input, so a <label for> can point at it. */
  inputId?: string;
}>();

const emit = defineEmits<{ (e: "update:modelValue", val: Item | null): void }>();

const listId = `select-${++uid}`;
const inputEl = ref<HTMLInputElement | null>(null);
const query = ref("");
const open = ref(false);
const active = ref(0);
const localSelected = ref<Item | null>(props.modelValue ?? null);
const localItems = ref<Item[]>([...(props.items ?? [])]);

watch(() => props.modelValue, (val) => { localSelected.value = val ?? null; });
watch(() => props.items, (val) => { localItems.value = [...(val ?? [])]; });
watch(query, () => { active.value = 0; });

const normalize = (s: string) => String(s ?? "").trim().toLowerCase();
const keyOf = (item: Item) => item.id ?? normalize(item.value);
// Values loaded from the API sometimes arrive as {title} or {name}; show whichever is there.
const labelOf = (item: Item | null) => item?.value ?? item?.title ?? item?.name ?? "";
const selectedLabel = computed(() => labelOf(localSelected.value));

const filteredItems = computed(() => {
  const q = normalize(query.value);
  const list = q ? localItems.value.filter((i) => normalize(i.value).includes(q)) : localItems.value;
  return list.slice(0, MAX_SHOWN);
});

const exactMatch = computed(() => localItems.value.some((i) => normalize(i.value) === normalize(query.value)));
const canCreate = computed(() => query.value.trim() !== "" && !exactMatch.value);
const total = computed(() => filteredItems.value.length + (canCreate.value ? 1 : 0));

const optionId = (i: number) => `${listId}-opt-${i}`;
const activeId = computed(() => (open.value && total.value ? optionId(Math.min(active.value, total.value - 1)) : undefined));

const isSelected = (item: Item) => normalize(labelOf(localSelected.value)) === normalize(item.value);

function selectItem(item: Item | null) {
  localSelected.value = item;
  emit("update:modelValue", item);
  query.value = "";
  open.value = false;
}

function addCustom() {
  const val = query.value.trim();
  if (!val) return;
  const key = normalize(val);
  let item = localItems.value.find((i) => normalize(i.value) === key);
  if (!item) {
    item = { id: `custom:${key}`, value: val };
    localItems.value.push(item);
  }
  selectItem(item);
}

function choose(index: number) {
  if (index < filteredItems.value.length) selectItem(filteredItems.value[index]);
  else if (canCreate.value) addCustom();
}

function scrollActive() {
  nextTick(() => document.getElementById(optionId(active.value))?.scrollIntoView({ block: "nearest" }));
}

function onFocus() {
  query.value = "";
  open.value = true;
  // Start on the current choice so Enter keeps it and the arrows move from it.
  const current = filteredItems.value.findIndex(isSelected);
  active.value = current >= 0 ? current : 0;
  scrollActive();
}

function onInput(e: Event) {
  query.value = (e.target as HTMLInputElement).value;
  open.value = true;
}

function onKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case "ArrowDown":
      e.preventDefault();
      if (!open.value) open.value = true;
      else active.value = Math.min(active.value + 1, Math.max(total.value - 1, 0));
      scrollActive();
      break;
    case "ArrowUp":
      e.preventDefault();
      active.value = Math.max(active.value - 1, 0);
      scrollActive();
      break;
    case "Enter":
      e.preventDefault();
      if (!open.value) open.value = true;
      else if (total.value) choose(active.value);
      break;
    case "Escape":
      if (open.value) {
        e.preventDefault();
        open.value = false;
        query.value = "";
      }
      break;
  }
}

function onBlur() {
  window.setTimeout(() => {
    open.value = false;
    query.value = "";
  }, 150);
}
</script>
