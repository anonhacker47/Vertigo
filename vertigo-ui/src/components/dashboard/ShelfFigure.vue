<template>
  <div class="min-w-0">
    <span class="block text-[36px] font-black leading-none tracking-tight text-gray-50">
      <AnimatedNumber :number="value" /><span v-if="unit" class="ml-1.5 text-base font-bold tracking-normal text-slate-400">{{ unit }}</span>
    </span>
    <span class="mt-2 block text-[13px] font-semibold text-slate-400">{{ label }}</span>
    <div v-if="ratio !== null && ratio !== undefined" class="mt-2.5 h-1 overflow-hidden rounded-full bg-white/[.08]" aria-hidden="true">
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
