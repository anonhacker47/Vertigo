<template>
  <div class="relative w-full">
    <div class="fm-input fm-tokens" @mousedown="onContainerMouseDown">
      <span v-for="item in visibleSelected" :key="keyOf(item)" class="fm-chip" :title="item.value">
        <span class="truncate">{{ item.value }}</span>
        <button
          type="button"
          class="fm-chip__remove"
          :aria-label="`Remove ${item.value}`"
          tabindex="-1"
          @mousedown.prevent.stop
          @click.stop="removeItem(item)"
        >
          <i class="pi pi-times" style="font-size: 9px"></i>
        </button>
      </span>
      <button
        v-if="hiddenCount"
        type="button"
        class="fm-chip fm-chip--more"
        :aria-label="`Show ${hiddenCount} more selected`"
        tabindex="-1"
        @mousedown.prevent.stop
        @click.stop="expanded = true"
      >
        +{{ hiddenCount }} more
      </button>
      <button
        v-else-if="expanded && localSelected.length > COLLAPSED_LIMIT"
        type="button"
        class="fm-chip fm-chip--more"
        tabindex="-1"
        @mousedown.prevent.stop
        @click.stop="expanded = false"
      >
        Show fewer
      </button>
      <input
        :id="inputId"
        ref="inputEl"
        v-model="query"
        class="fm-tokens__input"
        :placeholder="localSelected.length ? '' : placeholder"
        role="combobox"
        :aria-expanded="open"
        :aria-controls="listId"
        :aria-activedescendant="activeId"
        aria-autocomplete="list"
        autocomplete="off"
        @focus="open = true"
        @input="open = true"
        @blur="onBlur"
        @keydown="onKeydown"
      />
    </div>

    <ul v-if="open && total" :id="listId" role="listbox" aria-multiselectable="true" class="fm-menu">
      <li
        v-for="(item, i) in filteredItems"
        :id="optionId(i)"
        :key="keyOf(item)"
        role="option"
        :aria-selected="isSelected(item)"
        class="fm-menu__item"
        :class="{ 'is-active': i === active, 'is-checked': isSelected(item) }"
        @mousedown.prevent="toggleItem(item)"
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

type Item = { id: any; value: string };

let uid = 0;
const MAX_SHOWN = 100;
// Chips shown before the rest collapse behind "+N more", so a big import stays one or two lines.
const COLLAPSED_LIMIT = 6;

const props = defineProps<{
  field?: string;
  placeholder?: string;
  items: Item[];
  modelValue: Item[];
  /** id for the text input, so a <label for> can point at it. */
  inputId?: string;
}>();

const emit = defineEmits<{ (e: "update:modelValue", val: Item[]): void }>();

const listId = `multiselect-${++uid}`;
const inputEl = ref<HTMLInputElement | null>(null);
const query = ref("");
const open = ref(false);
const active = ref(0);
const expanded = ref(false);
const localSelected = ref<Item[]>([...(props.modelValue ?? [])]);
const localItems = ref<Item[]>([...(props.items ?? [])]);

// Only sync in when the parent value actually changes (for example a form reset or an import).
watch(() => props.modelValue, (val) => { localSelected.value = [...(val ?? [])]; });
watch(() => props.items, (val) => { localItems.value = [...(val ?? [])]; });
watch(query, () => { active.value = 0; });

const normalize = (s: string) => String(s ?? "").trim().toLowerCase();
const keyOf = (item: Item) => item.id ?? normalize(item.value);

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

const isSelected = (item: Item) => localSelected.value.some((i) => normalize(i.value) === normalize(item.value));

const visibleSelected = computed(() => (expanded.value ? localSelected.value : localSelected.value.slice(0, COLLAPSED_LIMIT)));
const hiddenCount = computed(() => localSelected.value.length - visibleSelected.value.length);

function commit(next: Item[]) {
  localSelected.value = next;
  emit("update:modelValue", next);
}

function toggleItem(item: Item) {
  if (isSelected(item)) removeItem(item);
  else commit([...localSelected.value, item]);
  query.value = "";
  nextTick(() => inputEl.value?.focus());
}

function removeItem(item: Item) {
  commit(localSelected.value.filter((i) => normalize(i.value) !== normalize(item.value)));
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
  if (!isSelected(item)) toggleItem(item);
  else query.value = "";
}

function choose(index: number) {
  if (index < filteredItems.value.length) toggleItem(filteredItems.value[index]);
  else if (canCreate.value) addCustom();
}

function scrollActive() {
  nextTick(() => document.getElementById(optionId(active.value))?.scrollIntoView({ block: "nearest" }));
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
      }
      break;
    case "Backspace":
      if (!query.value && localSelected.value.length) removeItem(localSelected.value[localSelected.value.length - 1]);
      break;
  }
}

function onContainerMouseDown(e: MouseEvent) {
  if (e.target === inputEl.value) return;
  e.preventDefault();
  inputEl.value?.focus();
  open.value = true;
}

function onBlur() {
  window.setTimeout(() => {
    open.value = false;
    query.value = "";
  }, 150);
}
</script>
