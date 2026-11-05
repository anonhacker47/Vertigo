<template>
  <div class="cover" :class="{ 'cover--dim': dim }">
    <img v-if="src && !failed" :src="src" :alt="alt" decoding="async" draggable="false" @error="failed = true" />
    <div v-else class="cover__fallback" :style="{ background: placeholderGradient(title) }" role="img" :aria-label="alt || title">
      <span>{{ placeholderInitials(title) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { placeholderGradient, placeholderInitials } from "@/utils/placeholderGradient";

const props = withDefaults(defineProps<{ src?: string | null; title: string; alt?: string; dim?: boolean }>(), {
  src: null,
  alt: "",
  dim: false,
});

const failed = ref(false);
watch(() => props.src, () => { failed.value = false; });
</script>

<style scoped>
.cover {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: 5px;
  background: #161617;
  box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.06);
}
.cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
/*
 * Shade for the covers either side, and a faint sheen for the one in front. Both are overlays
 * whose opacity animates, which the compositor handles without repainting the artwork.
 */
.cover::before,
.cover::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.cover::before {
  background: rgba(8, 12, 24, 0.5);
  opacity: 0;
}
.cover--dim::before { opacity: 1; }
.cover::after {
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.14), transparent 42%);
  opacity: 1;
}
.cover--dim::after { opacity: 0; }
.cover__fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 40px;
  font-weight: 900;
  letter-spacing: 0.02em;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}
@media (prefers-reduced-motion: reduce) {
  .cover::before,
  .cover::after { transition: none; }
}
</style>
