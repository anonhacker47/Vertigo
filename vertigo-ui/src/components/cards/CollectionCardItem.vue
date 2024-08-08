<template>
  <RouterLink class="shadow-2xl pt-4 flex flex-grow"
    :class="[`md:h-[${cardHeightMD}rem]`, `md:w-[${cardWidthMD}rem]`, `h-[${cardHeight}rem]`, `w-[${cardWidth}rem]`]"
    :to="{
      name: 'series',
      params: { Link: card.slug, Id: card.id },
      id: card.id,
    }">
    <div class="flex items-end" @mouseenter="activate" @mouseleave="activate">
      <div class="flex h-full w-full items-end">
        <div id="image_container"
          class="h-full rounded flex-col relative md:rounded-lg w-full justify-end hvr-bounce-in items-center text-center">
          <img v-if="displayedImage !== Image" :src="displayedImage" @error="handleImageError" alt=""
            class="slideritem h-full w-full md:rounded-t" />

          <div class="absolute flex h-full w-full rounded-t md:rounded-t bg-[#131929] opacity-0"
            :class="{ 'opacity-60': active }">
          </div>
          <span v-if="active || displayedImage == Image"
            class="absolute md:text-xl name text-sm leading-none font-bold uppercase pb-2 break-words text-ellipsis whitespace-nowrap overflow-hidden w-[80%]"
            :class="(displayedImage == Image ? 'top-1/2' : '',
                      `md:max-w-[${textwidthMD / 2}vw]`,
                      `max-w-[${textwidth / 2}vw]`)
                  " :style="displayedImage == Image ? `top: 50%;` : ''">
            {{ card.title }}
          </span>
          <span
            class="absolute text-[12px] md:text-[12x] m-[3px] px-[4px] font-bold text-sm bg-slate-800 text-green-200 text rounded top-0 right-0 break-words">
            {{ card.series_format }}
          </span>
          <div class="h-3 w-full relative">
            <div class="h-full bg-sky-500 rounded-b absolute" :style="{ width: fraction(card.owned_count, card.issue_count) }">
            </div>
            <div class="h-full bg-green-400 rounded-b absolute" :style="{ width: fraction(card.read_count, card.issue_count) }">
            </div>
          </div>
        </div>
      </div>
      <TransitionGroup enter-active-class="animate__animated animate__bounceIn"
        leave-active-class="animate__animated animate__bounceOut">
        <div v-if="deleteMode" @click.prevent="confirmDelete(card.id, card.title)"
          class="absolute top-0 right-0 rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
          <img src="@/assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
        </div>
      </TransitionGroup>
    </div>
  </RouterLink>
</template>

<script setup>
import { defineProps, defineEmits, ref } from 'vue';
import SeriesService from '@/services/SeriesService';

const props = defineProps({
  card: Object,
  cardHeightMD: Number,
  cardWidthMD: Number,
  cardHeight: Number,
  cardWidth: Number,
  deleteMode: Boolean,
});

const emit = defineEmits(['confirmDelete']);

const displayedImage = ref(SeriesService.getImagebyId(props.card.id));
const Image = "noimage";

const active = ref(false);

const handleImageError = () => {
  displayedImage.value = Image;
};

function activate() {
  active.value = !active.value;
}

function fraction(count, total) {
  return `${(count / total) * 100}%`;
}

function confirmDelete(id, title) {
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
