<template>
                  <div class="inline-block px-3">
                    <div
                      class="md:h-[35vh] flex md:w-[12vw] rounded-lg ml-4 border-2 justify-center bg-cover items-center transition-shadow duration-300 ease-in-out"
                      :style="`background-image: ${
                        'url(' + image + ')'
                      }; border-color: rgb${themecolor}`"
                    >
                      <div
                        class="h-full w-full justify-center items-center rounded-lg flex"
                        :style="`background: rgba(25,18,43,0.7);`"
                      >
                        <p
                          class="md:text-xl text-white text-sm leading-none uppercase pb-2 break-words"
                        >
                          {{ title }}
                        </p>
                      </div>
                    </div>
                  </div>
</template>

<script setup>

const props = defineProps({
    image:String,
    themecolor:String,
    title:String
})

</script>

<style scoped>

</style>