<template>
  <div class="h-44 w-28 flex flex-col rounded-lg border-2" :style="`border-color: rgb${themecolor};`">
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
      <div class="flex basis-1/2 border-r-2 justify-center" :style="`border-color: rgb${themecolor};`"> 
        <img class="cursor-pointer" src="../../assets/collection.svg" alt="" width="20" height="20" />
      </div>
      <div class="flex basis-1/2 justify-center"> 
        <img class="cursor-pointer" src="../../assets/read.svg" alt="" width="23" height="23" />
      </div>
    </div>

  </div>
</template>

<script setup>

const props = defineProps({
  image: String,
  themecolor: String,
  title: String
})

</script>

<style scoped></style>