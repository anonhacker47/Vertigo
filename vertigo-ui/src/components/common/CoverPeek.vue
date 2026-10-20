<template>
  <Teleport to="body">
    <div v-if="peek" class="cover-peek" :style="{ left: `${peek.x}px`, top: `${peek.y}px` }" aria-hidden="true">
      <img :src="peek.src" alt="" />
      <span v-if="peek.caption" class="cover-peek__caption">{{ peek.caption }}</span>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const WIDTH = 204;
const HEIGHT = 324;
const GAP = 12;
const HOVER_DELAY_MS = 120;

const canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
const peek = ref<{ src: string; caption: string; x: number; y: number } | null>(null);
let timer = 0;

function place(target: HTMLElement, src: string, caption: string) {
  const rect = target.getBoundingClientRect();
  const fitsRight = rect.right + GAP + WIDTH <= window.innerWidth - 8;
  const x = fitsRight ? rect.right + GAP : Math.max(8, rect.left - GAP - WIDTH);
  const centred = rect.top + rect.height / 2 - HEIGHT / 2;
  const y = Math.min(Math.max(8, centred), window.innerHeight - HEIGHT - 8);
  peek.value = { src, caption, x, y };
}

/** Bind to mouseenter and focus: hover shows after a short delay on pointer devices, keyboard focus shows at once. */
function show(event: Event, src: string, caption = "") {
  const target = event.currentTarget as HTMLElement;
  window.clearTimeout(timer);
  if (event.type === "focus") {
    if (target.matches(":focus-visible")) place(target, src, caption);
    return;
  }
  if (!canHover) return;
  timer = window.setTimeout(() => place(target, src, caption), HOVER_DELAY_MS);
}

function hide() {
  window.clearTimeout(timer);
  peek.value = null;
}

onMounted(() => window.addEventListener("scroll", hide, { passive: true, capture: true }));
onBeforeUnmount(() => {
  window.removeEventListener("scroll", hide, { capture: true });
  hide();
});

defineExpose({ show, hide });
</script>

<style scoped>
.cover-peek {
  position: fixed;
  z-index: 1000;
  width: 204px;
  padding: 6px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #0b1220;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}
.cover-peek img {
  display: block;
  width: 192px;
  aspect-ratio: 2 / 3;
  border-radius: 4px;
  background: #1e293b;
  object-fit: cover;
}
.cover-peek__caption {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
  text-align: center;
}
</style>
