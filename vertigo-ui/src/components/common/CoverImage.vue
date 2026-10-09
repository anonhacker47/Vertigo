<template>
  <div class="hardcover relative bg-slate-800" :class="[aspect ? 'aspect-2/3 w-full' : '', `hardcover--${depth}`, { 'hardcover--lift': interactive }]">
    <div class="hardcover__face absolute inset-0 overflow-hidden">
      <img
        v-if="src && !failed"
        :src="src"
        :alt="alt ?? title"
        loading="lazy"
        decoding="async"
        class="absolute inset-0 h-full w-full object-cover"
        @error="failed = true"
      />
      <div
        v-else
        class="absolute inset-0 flex items-center justify-center text-white"
        :style="{ background: placeholderGradient(title) }"
        role="img"
        :aria-label="alt ?? title"
      >
        <span class="font-black tracking-wide drop-shadow" :class="initialsClass">{{ placeholderInitials(title) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { placeholderGradient, placeholderInitials } from "@/utils/placeholderGradient";

const props = withDefaults(
  defineProps<{
    src?: string | null;
    title: string;
    alt?: string;
    aspect?: boolean;
    depth?: "sm" | "md" | "lg";
    interactive?: boolean;
    initialsClass?: string;
  }>(),
  { src: null, aspect: true, depth: "md", interactive: true, initialsClass: "text-2xl" }
);

const failed = ref(false);
watch(() => props.src, () => { failed.value = false; });
</script>

<style scoped>
.hardcover {
  border-radius: 2px 6px 6px 2px;
  box-shadow: -4px 2px 4px 0 rgba(0, 0, 0, 0.3), -8px 8px 20px 0 rgba(0, 0, 0, 0.2);
  transition: transform 0.12s ease-out, box-shadow 0.12s ease-out;
}
.hardcover__face {
  border-radius: inherit;
}
.hardcover__face::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  border-radius: inherit;
  background-image: linear-gradient(to right,
    rgba(0, 0, 0, 0.2),
    rgba(255, 255, 255, 0.3) 1%,
    transparent 6%,
    rgba(0, 0, 0, 0.15) 8%,
    rgba(255, 255, 255, 0.2) 9%,
    transparent 20%);
  box-shadow: inset 1px 1px 0 1px rgba(255, 255, 255, 0.2), inset 0 0 0 1px rgba(0, 0, 0, 0.1);
}
.hardcover--sm {
  border-radius: 1px 4px 4px 1px;
  box-shadow: -2px 1px 3px 0 rgba(0, 0, 0, 0.3), -4px 4px 10px 0 rgba(0, 0, 0, 0.2);
}
.hardcover--lg {
  border-radius: 3px 8px 8px 3px;
  box-shadow: -6px 3px 8px 0 rgba(0, 0, 0, 0.35), -14px 14px 34px 0 rgba(0, 0, 0, 0.3);
}
.hardcover--lift:hover {
  transform: translateY(-4px) scale(1.03);
  box-shadow: -4px 4px 8px 0 rgba(0, 0, 0, 0.3), -12px 16px 30px 0 rgba(0, 0, 0, 0.3);
}
@media (prefers-reduced-motion: reduce) {
  .hardcover { transition: none; }
  .hardcover--lift:hover { transform: none; }
}
</style>
