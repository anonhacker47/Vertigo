<template>
<div class="flex flex-nowrap items-center">
  <div class="avatar">
  <div class="w-8 rounded">
    <img :src="icon" alt="Tailwind-CSS-Avatar-component" />
  </div>
</div>
  <div class="flex flex-col ml-2">
    <div class="text-primary font-bold">
      {{field}}
    </div>
    <div class="text-xs font-medium">
      {{detail}}
    </div>
  </div>
</div>
</template>
<script setup>


const props = defineProps({
    icon :String,
    field : String,
    detail : String
})
</script>
<style>

</style>