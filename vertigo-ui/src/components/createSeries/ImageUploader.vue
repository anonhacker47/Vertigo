<template>
  <div class="flex flex-col gap-3">
    <div
      class="cover-drop"
      :class="{ 'cover-drop--over': dragOver }"
      @dragenter.prevent="dragOver = true"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <CoverImage
        :src="hasImage ? imagesrc : null"
        :title="title ?? ''"
        alt="Cover preview"
        depth="lg"
        :interactive="false"
        initials-class="text-4xl"
        @error="changeThumb"
      />
      <label class="cover-drop__overlay" :class="{ 'cover-drop__overlay--empty': !hasImage }">
        <i class="pi pi-upload" style="font-size: 18px"></i>
        <span>{{ hasImage ? "Replace cover" : "Upload a cover" }}</span>
        <span class="cover-drop__sub">or drop an image here</span>
        <input type="file" accept="image/*" class="sr-only" @change="onFileInput" />
      </label>
    </div>

    <p v-if="fileName" class="fm-hint truncate text-center" :title="fileName">Using {{ fileName }}</p>

    <label class="block">
      <span class="fm-label">Cover link</span>
      <input v-model="imageLinkInput" type="text" class="fm-input" placeholder="https://" autocomplete="off" @input="onLinkInput" />
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import CoverImage from "@/components/common/CoverImage.vue";

const props = defineProps<{
  modelValue: string;
  imageLink?: string;
  title?: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "image-change", file: File | string): void;
}>();

const dummy = new URL("../../assets/dummy.webp", import.meta.url).href;
const imagesrc = ref<string>(props.modelValue || dummy);
const imageLinkInput = ref(props.imageLink || "");
const fileName = ref("");
const dragOver = ref(false);

const hasImage = computed(() => !!imagesrc.value && imagesrc.value !== dummy);

watch(() => props.imageLink, (val) => {
  imageLinkInput.value = val || "";
  fileName.value = "";
  emit("image-change", val ?? "");
});

watch(() => props.modelValue, (val) => {
  if (val && val !== imagesrc.value) imagesrc.value = val;
});

function applyFile(file: File) {
  imagesrc.value = URL.createObjectURL(file);
  fileName.value = file.name;
  imageLinkInput.value = "";
  emit("image-change", file);
}

function onFileInput(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) applyFile(file);
  // Reset so choosing the same file again still fires a change event.
  input.value = "";
}

function onDrop(event: DragEvent) {
  dragOver.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file && file.type.startsWith("image/")) applyFile(file);
}

function onLinkInput() {
  const url = imageLinkInput.value.trim() || dummy;
  imagesrc.value = url;
  fileName.value = "";
  emit("update:modelValue", url);
  emit("image-change", url);
}

function changeThumb() {
  imagesrc.value = dummy;
  emit("image-change", "noimage");
}
</script>

<style scoped>
.cover-drop {
  position: relative;
}
.cover-drop__overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  border-radius: 3px 8px 8px 3px;
  background: rgba(11, 18, 32, 0.76);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  text-align: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s ease;
}
.cover-drop:hover .cover-drop__overlay,
.cover-drop__overlay:focus-within,
.cover-drop--over .cover-drop__overlay,
.cover-drop__overlay--empty {
  opacity: 1;
}
.cover-drop__overlay--empty {
  background: rgba(11, 18, 32, 0.38);
}
.cover-drop--over .cover-drop__overlay {
  outline: 2px dashed #38bdf8;
  outline-offset: -8px;
}
.cover-drop__overlay:focus-within {
  outline: 2px solid #38bdf8;
  outline-offset: -4px;
}
.cover-drop__sub {
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
}
@media (prefers-reduced-motion: reduce) {
  .cover-drop__overlay { transition: none; }
}
</style>
