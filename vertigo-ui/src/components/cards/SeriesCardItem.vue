<template>
  <div class="flex items-end" @mouseenter="activate" @mouseleave="activate">
    <div class="flex h-full w-full items-end">
      <div id="image_container"
        class="h-full rounded md:rounded-lg w-full justify-center hvr-bounce-in items-end text-center border-solid border-b-[12px] border-green-400">
        <img v-if="src != Image" :src="localSrc" @error="localSrc = Image" alt=""
          class="slideritem h-full w-full md:rounded-t-lg" />

        <div class="absolute flex h-full w-full rounded-t md:rounded-t-lg bg-[#131929] opacity-0"
          :class="{ 'opacity-60': active }"></div>
        <p v-if="active || src == Image"
          class="absolute md:text-xl name text-sm leading-none uppercase pb-2 break-words" :class="[
            src == Image ? 'top-1/2' : '',
            `md:max-w-[${textwidthMD / 2}vw]`,
            `max-w-[${textwidth / 2}vw]`
          ]" :style="src == Image ? `top: 50%;` : ''">
          {{ name }}
        </p>
        <p
          class="absolute text-[10px] md:text-sm font-bold px-3 py-2 m-1 md:m-2 bg-slate-800 text-green-200 rounded md:rounded-md top-0 right-0 break-words">
          {{ format }}
        </p>
      </div>
    </div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref,watch } from "vue";

onMounted(() => { });

const props = defineProps({
  name: String,
  src: String,
  format: String,
  textwidth: Number,
  textwidthMD: Number,
});

let Image = "noimage";
const localSrc = ref(props.src);
const active = ref(false);

watch(() => props.src, (newSrc) => {
  localSrc.value = newSrc;
});


function activate() {
  active.value = !active.value;
}
</script>

<style scoped>
#image_container {
  display: flex;
  background-color: #161617;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  z-index: 8;
}

.slideritem {
  background-repeat: no-repeat;
  background-size: cover;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
}

#image_container:hover {
  /* box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22); */
  /* transform: rotate3d(0.5, -0.866, 0, 15deg) rotate(2deg); */
  cursor: pointer;
}

.hvr-bounce-in:hover,
.hvr-bounce-in:focus,
.hvr-bounce-in:active {
  -webkit-transform: scale(1.05);
  transform: scale(1.05);
  -webkit-transition-timing-function: ease-in-out;
  transition-timing-function: ease-in-out;
}

.name {
  color: white;
  font-weight: 700;
}
</style>
