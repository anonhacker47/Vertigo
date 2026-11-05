<template>
  <!-- A tick per bucket of items in the box; divider ticks stand taller and carry their label when there is room. -->
  <div ref="root" class="scrub" aria-hidden="true" @pointerdown="onPointerDown" @pointermove="onPointerMove" @pointerup="onPointerUp" @pointercancel="onPointerUp">
    <div class="ticks">
      <i v-for="tick in ticks" :key="tick.start" :class="{ d: tick.divider, cur: tick.current }" :data-l="tick.label"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import type { LongboxItem } from "./dividers";

const props = defineProps<{ items: LongboxItem[]; current: number }>();
const emit = defineEmits<{ (e: "update:current", index: number): void }>();

/** Pixels a divider label needs before the next one may be shown. */
const LABEL_GAP = 56;
/** Width a tick needs, so a big collection is bucketed instead of drawn one element per series. */
const TICK_PX = 4;
/** Ticks drawn before the strip has been measured. */
const TICKS_UNMEASURED = 200;

const root = ref<HTMLElement | null>(null);
const width = ref(0);
let observer: ResizeObserver | null = null;
onMounted(() => {
  observer = new ResizeObserver(([entry]) => { width.value = entry.contentRect.width; });
  if (root.value) observer.observe(root.value);
});
onBeforeUnmount(() => observer?.disconnect());

// Items grouped into as many ticks as the strip has room for. A bucket is a divider tick when it
// holds one, and the current tick is the bucket the front item falls in.
const ticks = computed(() => {
  const count = props.items.length;
  const maxTicks = width.value ? Math.max(40, Math.floor(width.value / TICK_PX)) : TICKS_UNMEASURED;
  const size = Math.max(1, Math.ceil(count / maxTicks));
  const perTick = width.value / Math.ceil(count / size) || 0;
  const out: { start: number; divider: boolean; current: boolean; label: string }[] = [];
  let lastLabeled = -Infinity;
  for (let start = 0; start < count; start += size) {
    const end = Math.min(count, start + size);
    let divider: LongboxItem | undefined;
    for (let i = start; i < end && !divider; i++) {
      if (props.items[i]?.kind === "divider") divider = props.items[i];
    }
    let label = "";
    if (divider?.kind === "divider" && (out.length - lastLabeled) * perTick >= LABEL_GAP) {
      label = divider.label;
      lastLabeled = out.length;
    }
    out.push({ start, divider: !!divider, current: props.current >= start && props.current < end, label });
  }
  return out;
});

let scrubbing = false;
function scrubTo(event: PointerEvent) {
  if (!root.value || !props.items.length) return;
  const rect = root.value.getBoundingClientRect();
  const fraction = Math.max(0, Math.min(0.9999, (event.clientX - rect.left) / rect.width));
  const index = Math.floor(fraction * props.items.length);
  if (index !== props.current) emit("update:current", index);
}
function onPointerDown(event: PointerEvent) {
  if (event.button !== 0) return;
  scrubbing = true;
  root.value?.setPointerCapture(event.pointerId);
  scrubTo(event);
}
function onPointerMove(event: PointerEvent) {
  if (scrubbing) scrubTo(event);
}
function onPointerUp() {
  scrubbing = false;
}
</script>

<style scoped>
.scrub {
  position: relative;
  height: 44px;
  margin-top: 6px;
  padding-top: 20px;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
  touch-action: none;
}
.ticks {
  display: flex;
  align-items: flex-end;
  height: 20px;
  gap: 1px;
  padding: 0 2px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.ticks i {
  position: relative;
  flex: 1 1 0;
  min-width: 0;
  height: 6px;
  border-radius: 1px 1px 0 0;
  background: rgba(255, 255, 255, 0.1);
  transition: background 0.15s, height 0.15s;
}
.ticks i.d { height: 12px; background: rgba(255, 255, 255, 0.28); }
.ticks i.cur { height: 20px; background: #38bdf8; }
.ticks i.d::after {
  content: attr(data-l);
  position: absolute;
  left: 0;
  bottom: 15px;
  font-size: 11px;
  font-style: normal;
  font-weight: 800;
  color: #64748b;
  white-space: nowrap;
}
.scrub:hover .ticks i:not(.cur):hover { background: rgba(255, 255, 255, 0.45); }
@media (prefers-reduced-motion: reduce) {
  .ticks i { transition: none; }
}
</style>
