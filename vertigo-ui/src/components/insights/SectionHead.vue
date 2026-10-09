<template>
  <div class="mb-4 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-2">
    <h2 class="text-2xl font-extrabold text-white">
      {{ title }}
      <small v-if="subtitle" class="ml-2 text-[15px] font-semibold text-slate-400">{{ subtitle }}</small>
    </h2>
    <div v-if="$slots.default" class="flex items-center gap-3 text-sm font-semibold text-slate-400">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>();
</script>
