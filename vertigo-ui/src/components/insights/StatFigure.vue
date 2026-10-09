<template>
  <div class="min-w-0">
    <span class="mb-2 block text-[13px] font-bold text-slate-400">{{ label }}</span>
    <span class="block leading-none font-black tracking-tight text-white" :class="compact ? 'text-[26px]' : 'text-[40px]'">{{ value }}</span>
    <span v-if="detail || $slots.default" class="mt-2 block text-sm font-semibold text-slate-300">
      <slot>{{ detail }}</slot>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string | number; detail?: string; compact?: boolean }>();
</script>
