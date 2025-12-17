<template>
  <RouterLink
    :to="to"
    class="bg-slate-800 px-3 py-1 rounded text-sm border border-slate-600 font-bold inline-block hover:bg-slate-700 transition"
    :style="`color: rgb${color}`"
  >
    {{ label }}
  </RouterLink>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  to: {
    type: [String, Object],
    required: true,
  },
  color: {
    type: String,
    default: '(255,255,255)',
  },
})
</script>
