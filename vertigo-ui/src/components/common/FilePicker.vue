<template>
  <div class="picker" :class="{ 'picker--over': over, 'picker--disabled': disabled, 'picker--filled': !!modelValue }"
    @dragenter.prevent="setOver(true)" @dragover.prevent="setOver(true)" @dragleave.prevent="setOver(false)"
    @drop.prevent="onDrop">
    <input ref="input" type="file" :accept="accept" class="sr-only" :disabled="disabled" @change="onChange" />

    <template v-if="modelValue">
      <span class="picker__icon" aria-hidden="true"><i class="pi pi-file"></i></span>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-semibold text-slate-100" :title="modelValue.name">{{ modelValue.name }}</p>
        <p class="text-xs text-slate-400">{{ formatBytes(modelValue.size) }}</p>
      </div>
      <Button type="button" label="Change" size="small" text severity="secondary" :disabled="disabled" @click="open" />
      <Button type="button" icon="pi pi-times" size="small" text severity="secondary" aria-label="Remove file"
        :disabled="disabled" @click="clear" />
    </template>

    <template v-else>
      <span class="picker__icon" aria-hidden="true"><i class="pi pi-upload"></i></span>
      <div class="min-w-0 flex-1">
        <p class="text-sm text-slate-200">
          <button type="button" class="picker__browse" :disabled="disabled" @click="open">{{ label }}</button>
          <span class="text-slate-400"> or drop it here</span>
        </p>
        <p v-if="hint" class="mt-0.5 text-xs text-slate-500">{{ hint }}</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Button from "primevue/button";
import { formatBytes } from "@/utils/download";

withDefaults(defineProps<{
  modelValue: File | null;
  accept: string;
  hint?: string;
  label?: string;
  disabled?: boolean;
}>(), { label: "Choose a file", disabled: false });

const emit = defineEmits<{ (e: "update:modelValue", file: File | null): void }>();

const input = ref<HTMLInputElement | null>(null);
const over = ref(false);

function setOver(value: boolean) {
  over.value = value;
}

function open() {
  input.value?.click();
}

function clear() {
  emit("update:modelValue", null);
}

function onChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0] ?? null;
  if (file) emit("update:modelValue", file);
  // Reset so choosing the same file again still fires a change event.
  target.value = "";
}

function onDrop(event: DragEvent) {
  over.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) emit("update:modelValue", file);
}
</script>

<style scoped>
.picker {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  background: rgba(2, 6, 23, 0.35);
  transition: border-color 0.12s ease, background-color 0.12s ease;
}
.picker--filled {
  border-style: solid;
  border-color: rgba(148, 163, 184, 0.25);
}
.picker--over {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.06);
}
.picker--disabled {
  opacity: 0.6;
}
.picker__icon {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
  font-size: 15px;
}
.picker--filled .picker__icon {
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
}
.picker__browse {
  font-weight: 700;
  color: #7dd3fc;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.picker__browse:hover {
  color: #bae6fd;
}
.picker__browse:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
  border-radius: 4px;
}
.picker__browse:disabled {
  cursor: default;
  text-decoration: none;
}
</style>
