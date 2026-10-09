<template>
  <div class="seg" role="group" :aria-label="label">
    <button
      v-for="option in options"
      :key="String(option.value)"
      type="button"
      :aria-pressed="option.value === modelValue"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
export interface SegmentedOption<T = string> {
  label: string;
  value: T;
}

defineProps<{
  modelValue: string;
  options: SegmentedOption[];
  label: string;
  size?: "sm" | "md";
}>();
defineEmits<{ (e: "update:modelValue", value: string): void }>();
</script>

<style scoped>
.seg {
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  border-radius: 10px;
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.seg button {
  min-height: 30px;
  padding: 0 11px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 700;
  color: #94a3b8;
  white-space: nowrap;
  transition: color 0.12s ease, background-color 0.12s ease;
}
.seg button:hover { color: #cbd5e1; }
.seg button[aria-pressed="true"] { background: #1e293b; color: #fff; }
.seg button:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
</style>
