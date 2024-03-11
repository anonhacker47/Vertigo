<template>
  <div class="flex items-end" @mouseenter="activate" @mouseleave="activate">
    <div class="flex h-full w-full items-end">
      <div
        id="image_container"
        class="h-full rounded flex-col md:rounded-lg w-full justify-end hvr-bounce-in items-center text-center"
      >
        <img
        v-if="displayedImage !== Image"
          :src="displayedImage"
          @error="handleImageError"
          alt=""
          class="slideritem h-full w-full md:rounded-t"
        />

        <div
          class="absolute flex h-full w-full rounded-t md:rounded-t bg-[#131929] opacity-0"
          :class="{ 'opacity-60': active }"
        >
      </div>
        <span
          v-if="active || displayedImage == Image"
          class="absolute md:text-xl name text-sm leading-none uppercase pb-2 break-words text-ellipsis whitespace-nowrap overflow-hidden w-[80%]"
          :class="
            (displayedImage == Image ? 'top-1/2' : '',
            `md:max-w-[${textwidthMD / 2}vw]`,
            `max-w-[${textwidth / 2}vw]`)
          "
          :style="displayedImage == Image ? `top: 50%;` : ''"
        >
          {{ name }}
        </span>
        <span
          class="absolute text-[9px] md:text-[12x] md:text-sm md:px-2 px-1 py-1 md:py-2 m-1 md:m-2 font-extrabold bg-slate-800 text-green-200 text rounded  top-0 right-0 break-words"
        >
          {{ format }}
        </span>
       <div class="h-3 w-full relative">
        <div class="h-full bg-sky-500 rounded-b absolute" :style="{ width: haveFraction }"></div>
        <div class="h-full bg-green-400 rounded-b absolute" :style="{ width: readFraction }"></div>
       </div>
      </div>
      
    </div> 
    
  </div>
  <!-- <span class="caption flex justify-center uppercase decoration-solid text-lg my-5">{{ name }}</span> -->
</template>

<script setup>
import { onMounted, ref } from "vue";

onMounted(() => {});

const props = defineProps({
  name: String,
  src: String,
  format: String,
  textwidth: Number,
  textwidthMD: Number,
  haveFraction: String,
  readFraction: String,
});

const displayedImage = ref(props.src);
let Image = "noimage";

const active = ref(false);

const handleImageError = () => {
      displayedImage.value = Image;
    };

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
