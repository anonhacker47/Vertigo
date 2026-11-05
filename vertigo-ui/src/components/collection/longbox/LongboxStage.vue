<template>
  <div ref="scene" class="scene" :style="{ '--w': `${coverWidth}px` }">
    <div class="glow" :style="{ backgroundColor: glowColor }" aria-hidden="true"></div>
    <div class="pool" aria-hidden="true"></div>
    <div class="floor" aria-hidden="true"></div>

    <div ref="stage" class="stage" tabindex="0" role="listbox"
      aria-label="Longbox. Arrow keys riffle through the series, Enter opens the one in front."
      :aria-activedescendant="activeId" @wheel.prevent="onWheel" @keydown="onKey"
      @pointerdown="onPointerDown" @pointermove="onPointerMove" @pointerup="onPointerUp" @pointercancel="onPointerCancel">
      <div v-for="entry in visible" :key="entry.item.id" :id="domId(entry.item)" class="item"
        :class="{ 'item--cur': entry.index === current }" role="option" :aria-selected="entry.index === current"
        :aria-label="entry.item.kind === 'series' ? entry.item.series.title : `${entry.item.label}, divider`"
        :style="entry.style" :data-index="entry.index">
        <LongboxCover v-if="entry.item.kind === 'series'" :src="entry.item.series.thumbnail" :title="entry.item.series.title" alt="" :dim="entry.index !== current" />
        <LongboxDivider v-else :label="entry.item.label" :count="entry.item.series.length" :image="entry.item.image" />
      </div>
    </div>

    <span class="hint" aria-hidden="true">Scroll, drag, or <kbd>←</kbd> <kbd>→</kbd></span>
    <span class="count">{{ countLabel }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import type { Series } from "@/types/series.types";
import type { LongboxItem } from "./dividers";
import LongboxCover from "./LongboxCover.vue";
import LongboxDivider from "./LongboxDivider.vue";

const props = withDefaults(defineProps<{ items: LongboxItem[]; current: number; pending?: number; glow?: [number, number, number] | null }>(), {
  pending: 0,
  glow: null,
});
const emit = defineEmits<{
  (e: "update:current", index: number): void;
  (e: "open", series: Series): void;
}>();

/** How many items either side of the front one get rendered; the rest are off in the dark anyway. */
const WINDOW = 12;
/** Horizontal drag distance that moves the row by one. */
const DRAG_STEP = 56;
/** Wheel travel per step, the most steps one wheel event may take, and the shortest gap between them. */
const WHEEL_STEP = 36;
const WHEEL_BURST = 3;
const WHEEL_INTERVAL = 40;
/** The glow when nothing is in front, or the front item has no colour: the page's own slate. */
const GLOW_DEFAULT = "rgb(51, 65, 85)";

const glowColor = computed(() => (props.glow ? `rgb(${props.glow[0]}, ${props.glow[1]}, ${props.glow[2]})` : GLOW_DEFAULT));

const scene = ref<HTMLElement | null>(null);
const stage = ref<HTMLElement | null>(null);

// Cover width follows the stage: a cover is 1.5× as tall as it is wide and needs headroom for a
// divider's tab and the front cover's perspective, and a narrow stage caps it lower still.
const coverWidth = ref(210);
let observer: ResizeObserver | null = null;
onMounted(() => {
  observer = new ResizeObserver(([entry]) => {
    const { width, height } = entry.contentRect;
    // a narrow stage sits the row lower (see the phone rule on .item), so it needs less headroom
    const byHeight = width < 640 ? (height - 100) / 1.5 : (height - 130) / 1.62;
    coverWidth.value = Math.round(Math.max(100, Math.min(width < 640 ? 150 : 210, byHeight)));
  });
  if (scene.value) observer.observe(scene.value);
  document.addEventListener("keydown", onDocumentKey);
});
onBeforeUnmount(() => {
  observer?.disconnect();
  document.removeEventListener("keydown", onDocumentKey);
});

// Left and right riffle from anywhere on the page while the longbox is open, so nobody has to
// know the stage takes focus. Typing fields and open menus keep their own arrow keys, and the
// stage's handler has already claimed the event when the stage itself is focused.
function onDocumentKey(event: KeyboardEvent) {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
  const target = event.target as HTMLElement | null;
  if (target?.closest("input, textarea, select, [contenteditable='true'], [role='dialog'], [role='menu'], [role='listbox']")) return;
  event.preventDefault();
  go(props.current + (event.key === "ArrowRight" ? 1 : -1));
}

const uid = Math.random().toString(36).slice(2, 8);
const domId = (item: LongboxItem) => `lb-${uid}-${item.id}`;
const activeId = computed(() => {
  const item = props.items[props.current];
  return item ? domId(item) : undefined;
});

// Cover-flow placement: the front item faces out, the others fan back on either side, spaced
// in proportion to the cover width.
function styleFor(d: number) {
  const ad = Math.abs(d);
  const w = coverWidth.value;
  const [first, step, angle] = [Math.round(w * 0.85), Math.round(w * 0.24), 58];
  const transform = d === 0
    ? "translate3d(0, 0, 170px) rotateY(0deg)"
    : `translate3d(${Math.sign(d) * (first + (ad - 1) * step)}px, 0, ${-ad * 16}px) rotateY(${d < 0 ? angle : -angle}deg)`;
  return { transform, zIndex: 100 - ad, opacity: d === 0 ? 1 : Math.max(0.25, 1 - ad * 0.07) };
}

const visible = computed(() => {
  const from = Math.max(0, props.current - WINDOW);
  const to = Math.min(props.items.length - 1, props.current + WINDOW);
  const out: { index: number; item: LongboxItem; style: Record<string, string | number> }[] = [];
  for (let index = from; index <= to; index++) {
    const item = props.items[index];
    if (item) out.push({ index, item, style: styleFor(index - props.current) });
  }
  return out;
});

// Ordinal of every series item, so the corner can say "14 of 240".
const ordinals = computed(() => {
  let n = 0;
  return props.items.map((item) => (item.kind === "series" ? ++n : 0));
});
const seriesTotal = computed(() => props.items.filter((item) => item.kind === "series").length);
const countLabel = computed(() => {
  const item = props.items[props.current];
  if (!item) return "";
  const more = props.pending ? `, loading ${props.pending} more` : "";
  if (item.kind === "divider") return `${item.label}${more}`;
  return `${ordinals.value[props.current]} of ${seriesTotal.value}${more}`;
});

function go(index: number) {
  const next = Math.max(0, Math.min(props.items.length - 1, index));
  if (next !== props.current) emit("update:current", next);
}
function openCurrent() {
  const item = props.items[props.current];
  if (item?.kind === "series") emit("open", item.series);
}
function nextDivider(direction: 1 | -1) {
  for (let i = props.current + direction; i >= 0 && i < props.items.length; i += direction) {
    if (props.items[i]?.kind === "divider") return i;
  }
  return direction > 0 ? props.items.length - 1 : 0;
}

// Wheel travel accumulates into steps: a mouse notch moves two or three covers, a trackpad moves
// one per WHEEL_STEP of travel, and bursts are spaced by WHEEL_INTERVAL so the row stays followable.
let wheelAcc = 0;
let wheelAt = 0;
let steppedAt = 0;
function onWheel(event: WheelEvent) {
  const now = performance.now();
  if (now - wheelAt > 200) wheelAcc = 0;
  wheelAt = now;
  wheelAcc += Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
  const steps = Math.max(-WHEEL_BURST, Math.min(WHEEL_BURST, Math.trunc(wheelAcc / WHEEL_STEP)));
  if (steps !== 0 && now - steppedAt >= WHEEL_INTERVAL) {
    go(props.current + steps);
    wheelAcc -= steps * WHEEL_STEP;
    steppedAt = now;
  }
}

function onKey(event: KeyboardEvent) {
  const handlers: Record<string, () => void> = {
    ArrowRight: () => go(props.current + 1),
    ArrowDown: () => go(props.current + 1),
    ArrowLeft: () => go(props.current - 1),
    ArrowUp: () => go(props.current - 1),
    Home: () => go(0),
    End: () => go(props.items.length - 1),
    PageDown: () => go(nextDivider(1)),
    PageUp: () => go(nextDivider(-1)),
    Enter: openCurrent,
    " ": openCurrent,
  };
  const handler = handlers[event.key];
  if (!handler) return;
  event.preventDefault();
  handler();
}

// A drag riffles; a tap on a side item brings it forward, a tap on the front cover opens it.
// The tapped item is captured on pointerdown because pointer capture retargets the later events.
let drag: { x: number; start: number; moved: boolean; hit: HTMLElement | null } | null = null;
function onPointerDown(event: PointerEvent) {
  if (event.button !== 0) return; // right and middle buttons keep their own meaning
  drag = { x: event.clientX, start: props.current, moved: false, hit: (event.target as HTMLElement).closest(".item") };
  stage.value?.setPointerCapture(event.pointerId);
}
function onPointerMove(event: PointerEvent) {
  if (!drag) return;
  const dx = event.clientX - drag.x;
  if (Math.abs(dx) > 6) drag.moved = true;
  go(drag.start - Math.round(dx / DRAG_STEP));
}
function onPointerUp() {
  if (drag && !drag.moved && drag.hit) {
    const index = Number(drag.hit.dataset.index);
    if (index === props.current) openCurrent();
    else go(index);
  }
  drag = null;
}
function onPointerCancel() {
  drag = null;
}
</script>

<style scoped>
.scene {
  --w: 210px;
  position: relative;
  height: var(--lb-h, 480px);
  overflow: hidden;
  user-select: none;
}

/*
 * Ambient light in the colour of the cover in front. A blurred solid shape: a colour change is a
 * cheap repaint of one ellipse and the blur stays on the GPU, where an animated gradient would
 * repaint the whole stage every frame.
 */
.glow {
  position: absolute;
  left: 50%;
  top: 48%;
  width: 56%;
  height: 54%;
  border-radius: 50%;
  transform: translate(-50%, -50%) translateZ(0);
  opacity: 0.38;
  filter: blur(70px);
  pointer-events: none;
  transition: background-color 0.7s ease;
  will-change: background-color;
}
/* a pool of shadow under the front cover, and the line the row stands on */
.pool {
  position: absolute;
  left: 50%;
  bottom: 42px;
  width: 440px;
  max-width: 90%;
  height: 56px;
  transform: translateX(-50%);
  pointer-events: none;
  background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.5), transparent 68%);
}
.floor {
  position: absolute;
  left: 4%;
  right: 4%;
  bottom: 70px;
  height: 1px;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.14) 25%, rgba(255, 255, 255, 0.14) 75%, transparent);
}

.stage {
  position: absolute;
  inset: 0;
  perspective: 1600px;
  perspective-origin: 50% 40%;
  cursor: grab;
  touch-action: pan-y;
  outline-offset: -3px;
  /* the far ends of the row fade out into the page */
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent);
}
.stage:active { cursor: grabbing; }
.stage:focus-visible { outline: 2px solid #38bdf8; border-radius: 10px; }

.item {
  position: absolute;
  left: calc(50% - var(--w) / 2);
  bottom: 72px;
  width: var(--w);
  transform-style: preserve-3d;
  transition: transform 0.32s cubic-bezier(0.2, 0.7, 0.2, 1), opacity 0.3s ease;
  will-change: transform, opacity;
  cursor: pointer;
}
.item--cur :deep(.cover) {
  box-shadow: 0 40px 80px -20px rgba(0, 0, 0, 0.75), 0 16px 32px -8px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.hint,
.count {
  position: absolute;
  top: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  pointer-events: none;
}
.hint { left: 4px; }
.count { right: 4px; font-variant-numeric: tabular-nums; color: #94a3b8; font-weight: 800; }
.hint kbd {
  display: inline-block;
  min-width: 20px;
  padding: 0 5px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  font: inherit;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
  color: #94a3b8;
}
/* on a phone the row stands lower in a shorter stage, and there is no room for the key hint */
@media (max-width: 639px) {
  .item { bottom: 44px; }
  .pool { bottom: 20px; }
  .floor { bottom: 42px; }
  .hint { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .glow,
  .item { transition: none; }
}
</style>
