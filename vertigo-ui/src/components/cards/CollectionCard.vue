<template>
  <RouterLink class="block w-full shadow-2xl" :class="{ 'animate-wiggle': deleteMode }"
    :to="{
      name: 'SeriesDetail',
      params: { Link: series.slug, Id: series.id },
    }">
    <div class="relative w-full" @mouseenter="activate" @mouseleave="activate">
      <div class="w-full">
        <div id="image_container"
          class="relative flex aspect-[2/3] w-full flex-col items-center justify-end rounded text-center hvr-bounce-in md:rounded-lg">
          <img v-if="displayedImage !== Image" loading="lazy" decoding="async" :src="displayedImage" @error="handleImageError" alt=""
            class="slideritem min-h-0 w-full flex-1 rounded-t-md object-cover md:rounded-t-md" />

          <div class="absolute flex h-full w-full rounded-t-md md:rounded-t-md bg-[#131929] opacity-0"
            :class="{ 'opacity-60': active }">
          </div>
          <span v-if="active || displayedImage == Image" :class="[
            'absolute md:text-xl name text-sm leading-none font-bold uppercase pb-2 break-words text-ellipsis whitespace-nowrap overflow-hidden w-[80%]',
            displayedImage == Image ? 'top-1/2' : ''
          ]" :style="displayedImage == Image ? `top: 50%;` : ''">
            {{ series.title }}
          </span>
          <span class="absolute right-2 top-2 max-w-[85%] truncate rounded-full border border-white/15 bg-slate-950/75 px-2 py-0.5 text-[11px] font-bold text-slate-200 backdrop-blur-sm">
            {{ series.series_format }}
          </span>
          <div class="relative h-3 w-full shrink-0 rounded-b-md bg-red-900">
            <div class="h-full bg-sky-500 rounded-b absolute"
              :style="{ width: fraction(series.owned_count, series.issue_count) }">
            </div>
            <div class="h-full bg-green-400 rounded-b absolute"
              :style="{ width: fraction(series.read_count, series.issue_count) }">
            </div>
          </div>
        </div>
      </div>
      <Transition enter-active-class="animate__animated animate__bounceIn"
        leave-active-class="animate__animated animate__bounceOut">
        <div v-if="deleteMode" @click.prevent="confirmDelete(series.id, series.title)"
          class="absolute -top-3 -right-3 rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
          <img src="@/assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
        </div>
      </Transition>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  series: Object,
  imageUrl: String,
  deleteMode: Boolean,
});

const emit = defineEmits(['confirmDelete']);

const displayedImage = ref(props.imageUrl);
const Image = "noimage";

const active = ref(false);

const handleImageError = () => {
  displayedImage.value = Image;
};

function activate() {
  active.value = !active.value;
}

function fraction(count: number, total: number) {
  return `${(count / total) * 100}%`;
}

function confirmDelete(id: number, title: string) {
  emit('confirmDelete', id, title);
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
  cursor: pointer;
}

.hvr-bounce-in:hover,
.hvr-bounce-in:focus,
.hvr-bounce-in:active {
  transform: scale(1.05);
  transition-timing-function: ease-in-out;
}

.name {
  color: white;
  font-weight: 700;
}
</style>
