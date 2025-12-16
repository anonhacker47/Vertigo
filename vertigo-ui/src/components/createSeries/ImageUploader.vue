<template>
  <div class="card w-full h-full bg-base-100 shadow-xl">
    <figure class="px-5 pt-5">
      <img :src="imagesrc" @error="changeThumb" alt="Invalid Link" class="rounded-xl h-full w-full max-h-[25rem]" />
    </figure>
    <div class="flex flex-col p-5">
      <div class="flex flex-col gap-2">
        <div class="form-control w-full">
          <label class="btn btn-primary w-full" for="file">
            Upload Image
          </label>
          <input type="file" @change="changeImage($event, 'file')" id="file" accept="image/*" style="display: none" />
        </div>
        <div class="flex justify-center">
          <p class="text-center font-bold">OR</p>
        </div>
        <div class="form-control w-full">
          <input id="image" type="text" v-model="imageLinkInput" @input="changeImage($event, 'url')"
            placeholder="paste image link here" class="input input-bordered w-full" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{
  modelValue: string;
}>();
const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "image-change", file: File | string): void;
}>();

const dummy = new URL("../../assets/dummy.webp", import.meta.url).href;
const imagesrc = ref<string>(props.modelValue || dummy);
const imageLinkInput = ref<string>("");

function changeImage(event: any, inputType: string) {
  let previewUrl = "";

  if (inputType === "file" && event.target.files && event.target.files[0]) {
    const file = event.target.files[0];
    previewUrl = URL.createObjectURL(file);

    // Update preview image
    imagesrc.value = previewUrl;

    // For displaying the filename in a text input, if needed
    imageLinkInput.value = file.name;

    // Emit the actual file object (used in FormData)
    emit("image-change", file);

    // Don't emit previewUrl here — let parent handle it separately if needed
  } else if (inputType === "url") {
    const url = event.target.value || dummy;

    imagesrc.value = url;

    emit("update:modelValue", url);
    emit("image-change", url);  // emit the URL string
  }
}

watch(() => props.modelValue, (val) => {
  if (val && val !== imagesrc.value) {
    imagesrc.value = val;
  }
});


function changeThumb() {
  imagesrc.value = dummy;
  emit("image-change", "noimage");
}
</script>