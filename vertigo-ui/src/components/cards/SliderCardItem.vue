<template>
  <div class="flex items-end" id="card">
    <div
      :style="{ height: cardHeight + 'vh', width: cardWidth + 'vw' }"
      class="flex items-start"
    >
      <div
        id="image_container"
        :style="{ height: cardHeight + 'vh', width: cardWidth + 'vw' }"
        class="flex overflow-hidden justify-center hvr-bounce-in items-end text-center border-solid border-b-[12px] border-green-400"
      >
        <!-- <div
      class="slideritem"
      :style="{ backgroundImage: 'url(' + src + ')' }"
    ></div> -->

        <img
          v-if="src != string"
          :src="src"
          alt=""
          class="slideritem"
        />

        <div
          class="absolute rounded-t-lg bg-[#131929] opacity-0 hover:opacity-50"
          :style="{ height: cardHeight + 'vh', width: cardWidth + 'vw' }"
          @mouseenter="activate"
          @mouseleave="activate"
        ></div>
        <p
          v-if="active || src == string"
          class="absolute name leading-none pb-2 break-words"
          :class="src == string?'top-1/2':''"
          :style="{ maxWidth: cardWidth - 2 + 'vw' }"
        >
          {{ name }}
        </p>
        <p
          class="absolute overflow-hidden px-3 py-2 m-2 bg-slate-800 text-green-200 font-bold rounded-md text-bold top-0 right-0 break-words"
        
        >
          {{ format }}
        </p>
      </div>
      <slot></slot>
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
  grid: Number,
});

let cardHeightMultiplier = [69, 62, 50, 41, 38];
let cardWidthMultiplier = [23, 20, 16, 13, 12];

let string = "string";
let cardHeight = cardHeightMultiplier[props.grid - 3];
let cardWidth = cardWidthMultiplier[props.grid - 3];

const active = ref(false);

function activate() {
  active.value = !active.value;
}
</script>

<style scoped>
#card {
  border-radius: 8px;
}

#image_container {
  display: flex;
  background-color: #161617;
  border-radius: 8px;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  z-index: 8;
}

.slideritem {
  height: 100%;
  width: 100%;
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
  font-size: 35px;
  font-weight: 700;
}
</style>
