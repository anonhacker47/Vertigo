<template>
<div class="flex flex-nowrap items-center">
  <div class="avatar">
  <div class="w-8 rounded">
    <img :src="icon" alt="Tailwind-CSS-Avatar-component" />
  </div>
</div>
  <div class="flex flex-col ml-2">
    <p class="text-xs font-bold">
      {{field}}
    </p>
    <p class="text-primary font-medium">
      {{detailString}}
    </p>
  </div>
</div>
</template>
<script setup lang="ts">
import { computed } from 'vue';



const props = defineProps({
    icon :String,
    field : String,
    detail: [String, Array]
  })

const detailString = computed(() => {
  return Array.isArray(props.detail) ? props.detail.join(", ") : props.detail;
});
</script>
<style>

</style>