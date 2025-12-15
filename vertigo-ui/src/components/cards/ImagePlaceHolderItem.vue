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

const props = defineProps({
  title: { type: String, required: true },
  size: { type: String as () => 'sm' | 'md' | 'lg', default: 'md' }
})

// --- hash function for deterministic gradient ---
function hashString(str: string) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = Math.trunc((Math.imul(31, h) + str.charCodeAt(i)))
  }
  return Math.abs(h)
}

const colors = [
  ['#8B5CF6', '#06B6D4'], // violet  cyan
  ['#F43F5E', '#F59E0B'], // rose  amber
  ['#3B82F6', '#06B6D4'], // blue  cyan
  ['#10B981', '#3B82F6'], // emerald  blue
  ['#EC4899', '#8B5CF6'], // pink  violet
  ['#F97316', '#EF4444'], // orange  red
  ['#14B8A6', '#0EA5E9'], // teal  sky
]

const gradient = computed(() => {
  if (!props.title) return 'linear-gradient(135deg, #444, #222)' // fallback

  const h = hashString(props.title)
  const palette = colors[h % colors.length]
  return `linear-gradient(135deg, ${palette[0]}, ${palette[1]})`
})

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
