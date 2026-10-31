<template>
  <!-- A column: number, caption, and the bar pinned to the bottom so bars line up across a row. -->
  <div class="flex min-w-0 flex-col">
    <span class="flex flex-wrap items-baseline gap-x-1.5 text-[36px] font-black leading-none tracking-tight text-gray-50">
      <AnimatedNumber :number="value" /><span v-if="unit" class="whitespace-nowrap text-base font-bold tracking-normal text-slate-400">{{ unit }}</span>
    </span>
    <span class="mt-2 block pb-2.5 text-[13px] font-semibold text-slate-400">{{ label }}</span>
    <div v-if="ratio !== null && ratio !== undefined" class="mt-auto h-1 overflow-hidden rounded-full bg-white/8" aria-hidden="true">
      <div class="h-full rounded-full transition-[width] duration-700" :class="tone === 'read' ? 'bg-green-400' : 'bg-sky-500'" :style="{ width: `${Math.min(100, Math.max(0, ratio))}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimatedNumber from "@/components/common/AnimatedNumber.vue";

withDefaults(
  defineProps<{
    value: number;
    unit?: string;
    label: string;
    ratio?: number | null;
    tone?: "owned" | "read";
  }>(),
  { unit: "", ratio: null, tone: "owned" }
);
</script>
