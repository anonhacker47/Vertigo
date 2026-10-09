<template>
  <div aria-hidden="true">
    <div v-if="variant === 'tiles'" class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-x-3 gap-y-5 md:grid-cols-[repeat(auto-fill,minmax(148px,1fr))] md:gap-x-[18px] md:gap-y-6">
      <div v-for="n in count" :key="n" class="flex flex-col gap-2">
        <div class="skeleton-block aspect-[2/3] w-full rounded-md"></div>
        <div class="skeleton-block h-3.5 w-4/5 rounded"></div>
        <div class="skeleton-block h-3 w-3/5 rounded"></div>
      </div>
    </div>
    <div v-else-if="variant === 'figures'" class="grid grid-cols-2 gap-5 md:grid-cols-4">
      <div v-for="n in count" :key="n" class="flex flex-col gap-2">
        <div class="skeleton-block h-3 w-1/2 rounded"></div>
        <div class="skeleton-block h-9 w-3/4 rounded"></div>
        <div class="skeleton-block h-3 w-2/3 rounded"></div>
      </div>
    </div>
    <div v-else-if="variant === 'chart'" class="skeleton-block h-56 w-full rounded-lg"></div>
    <div v-else-if="variant === 'hero'" class="grid items-center gap-7 md:grid-cols-[7fr_5fr] md:gap-10">
      <div class="flex flex-col gap-4">
        <div class="skeleton-block h-3 w-16 rounded"></div>
        <div class="skeleton-block h-20 w-40 rounded"></div>
        <div class="skeleton-block h-8 w-64 rounded"></div>
        <div class="skeleton-block h-4 w-72 rounded"></div>
        <div class="skeleton-block h-11 w-36 rounded-xl"></div>
      </div>
      <div class="skeleton-block h-[264px] w-[176px] justify-self-center rounded-lg md:h-[420px] md:w-[280px] md:justify-self-end"></div>
    </div>
    <div v-else class="flex flex-col gap-3">
      <div v-for="n in count" :key="n" class="skeleton-block h-4 rounded" :style="{ width: `${90 - n * 7}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ variant?: "tiles" | "figures" | "chart" | "hero" | "lines"; count?: number }>(), {
  variant: "lines",
  count: 4,
});
</script>

<style scoped>
.skeleton-block {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.05) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}
@keyframes shimmer {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton-block { animation: none; }
}
</style>
