<template>
  <div
    class="relative w-full flex items-center justify-center rounded-t-xl overflow-hidden border border-slate-700 shadow-lg"
    :class="sizeClass"
    :style="{
      background: gradient,
      color: '#ffffff'
    }"
  >
    <!-- subtle dot pattern overlay -->
    <svg
      class="absolute inset-0 w-full h-full opacity-[0.07] pointer-events-none"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      <defs>
        <pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="white" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dots)" />
    </svg>

    <!-- initials -->
    <span class="z-10 font-extrabold uppercase tracking-tight text-center" :class="initialSizeClass">
      {{ title }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { placeholderGradient } from '@/utils/placeholderGradient'

const props = defineProps({
  title: { type: String, required: true },
  size: { type: String as () => 'sm' | 'md' | 'lg', default: 'md' }
})

const gradient = computed(() => placeholderGradient(props.title))

// --- sizing ---
const sizeClass = computed(() => {
  return {
    sm: 'w-full h-16',
    md: 'w-full h-32',
    lg: 'w-full h-80'
  }[props.size]
})

const initialSizeClass = computed(() => {
  return {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl'
  }[props.size]
})
</script>
