<template>
  <div class="h-44 w-[7.5rem] flex flex-col rounded-lg border-2" :style="`border-color: rgb${themecolor};`">
    <div
      class="h-4/5 w-full flex flex-col rounded-lg justify-center bg-cover items-start transition-shadow duration-300 ease-in-out"
      :style="`background-image: ${'url(' + image + ')'
        };`">
      <div class="h-full w-full justify-center items-center rounded-lg flex" :style="`background: rgba(25,18,43,0.7);`">
        <p class=" text-white text-sm leading-none uppercase pb-2 break-words">
          {{ title }}
        </p>

      </div>
    </div>
    <div class="h-1/5 w-full flex rounded-b-lg border-t-2 " :style="`border-color: rgb${themecolor};`">
      <div class="flex basis-1/2 cursor-pointer border-r-2 justify-center" @click="$emit('updateStatus','is_owned')" :style="`border-color: rgb${themecolor};`"> 
        <img class="" :class="{ invert: !is_owned }" src="../../assets/collection.svg" alt="" width="22" height="22" />
      </div>
      <div class="flex basis-1/2 cursor-pointer justify-center" @click="$emit('updateStatus','is_read')"> 
        <img class="" :class="{ invert: !is_read  }"  src="../../assets/read.svg" alt="" width="20" height="20"  />
      </div>
    </div>

  </div>
</template>

<script setup>

const props = defineProps({
  image: String,
  themecolor: String,
  title: String,
  is_owned: Boolean,
  is_read: Boolean,
})


</script>

<style scoped>

</style>