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
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
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
/** Spring rate (1/s) when snapping to an item, and the slower rate a hard flick coasts at. */
const SNAP = 16;
const COAST = 4.5;
/** Release speed (items/s) that counts as a full flick, and the fastest one honoured. */
const FLICK = 10;
const MAX_SPEED = 80;
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
  halt();
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

// The row is drawn at a fractional index that a critically damped spring pulls to its target, so
// drags track the finger, flicks coast, and every other move (keys, wheel, scrubber) eases the same way.
const pos = ref(props.current);
let target = props.current;
let velocity = 0; // items per second
let omega = SNAP;
let frame = 0;
let lastFrame = 0;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function tick(now: number) {
  const dt = Math.max(0, Math.min(0.032, (now - lastFrame) / 1000));
  lastFrame = now;
  const x = pos.value - target;
  const push = (velocity + omega * x) * dt;
  const decay = Math.exp(-omega * dt);
  const next = (x + push) * decay;
  velocity = (velocity - omega * push) * decay;
  if (Math.abs(next) < 0.002 && Math.abs(velocity) < 0.05) {
    pos.value = target;
    velocity = 0;
    frame = 0;
    return;
  }
  pos.value = target + next;
  frame = requestAnimationFrame(tick);
}
function settle(to: number, rate = SNAP) {
  target = to;
  omega = rate;
  if (reducedMotion.matches) {
    halt();
    pos.value = to;
    velocity = 0;
  } else if (!frame) {
    lastFrame = performance.now();
    frame = requestAnimationFrame(tick);
  }
}
function halt() {
  cancelAnimationFrame(frame);
  frame = 0;
}
watch(() => props.current, (index) => {
  if (!drag && index !== target) settle(index);
});

// Cover-flow placement: the front item faces out, the others fan back on either side, spaced
// in proportion to the cover width. Within one step of the front the pose blends between the two.
function styleFor(d: number) {
  const ad = Math.abs(d);
  const side = Math.sign(d);
  const w = coverWidth.value;
  const [first, step, angle] = [w * 0.85, w * 0.24, 58];
  const t = Math.min(1, ad);
  const turn = t * t * (3 - 2 * t);
  const x = side * (ad <= 1 ? first * ad : first + (ad - 1) * step);
  const z = ad <= 1 ? 170 - 186 * turn : -ad * 16;
  return {
    transform: `translate3d(${x.toFixed(1)}px, 0, ${z.toFixed(1)}px) rotateY(${(-side * angle * turn).toFixed(1)}deg)`,
    zIndex: 1000 - Math.round(ad * 10),
    opacity: Math.max(0.25, 1 - ad * 0.07),
  };
}

const visible = computed(() => {
  const centre = Math.round(pos.value);
  const from = Math.max(0, centre - WINDOW);
  const to = Math.min(props.items.length - 1, centre + WINDOW);
  const out: { index: number; item: LongboxItem; style: Record<string, string | number> }[] = [];
  for (let index = from; index <= to; index++) {
    const item = props.items[index];
    if (item) out.push({ index, item, style: styleFor(index - pos.value) });
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

const clampIndex = (index: number) => Math.max(0, Math.min(props.items.length - 1, index));
function go(index: number) {
  const next = clampIndex(index);
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

// A drag riffles and a flick coasts; a tap on a side item brings it forward, a tap on the front
// cover opens it. The tapped item is captured on pointerdown because pointer capture retargets the later events.
let drag: { x: number; start: number; moved: boolean; hit: HTMLElement | null; samples: { t: number; p: number }[] } | null = null;
// side covers sit this far apart, so they follow the finger one to one
const dragStep = () => Math.max(28, coverWidth.value * 0.24);

function onPointerDown(event: PointerEvent) {
  if (event.button !== 0) return; // right and middle buttons keep their own meaning
  halt();
  velocity = 0;
  drag = { x: event.clientX, start: pos.value, moved: false, hit: (event.target as HTMLElement).closest(".item"), samples: [] };
  stage.value?.setPointerCapture(event.pointerId);
}
function onPointerMove(event: PointerEvent) {
  if (!drag) return;
  const dx = event.clientX - drag.x;
  if (Math.abs(dx) > 6) drag.moved = true;
  // past either end the row resists instead of stopping dead
  const max = props.items.length - 1;
  let p = drag.start - dx / dragStep();
  if (p < 0) p *= 0.35;
  else if (p > max) p = max + (p - max) * 0.35;
  pos.value = p;
  drag.samples.push({ t: event.timeStamp, p });
  while (drag.samples.length > 2 && event.timeStamp - drag.samples[0].t > 100) drag.samples.shift();
  go(Math.round(p));
}
function releaseSpeed(samples: { t: number; p: number }[], now: number) {
  const first = samples[0];
  const last = samples[samples.length - 1];
  if (!first || !last || last === first || now - last.t > 60 || last.t - first.t > 160) return 0;
  const speed = ((last.p - first.p) / (last.t - first.t)) * 1000;
  return Math.max(-MAX_SPEED, Math.min(MAX_SPEED, speed));
}
function onPointerUp(event: PointerEvent) {
  const released = drag;
  drag = null;
  if (!released) return;
  if (!released.moved) {
    const index = released.hit ? Number(released.hit.dataset.index) : props.current;
    if (released.hit && index === props.current) openCurrent();
    go(index);
    settle(clampIndex(index));
    return;
  }
  // the faster the flick, the slower the spring, so the row carries on before it settles
  velocity = releaseSpeed(released.samples, event.timeStamp);
  const rate = SNAP - (SNAP - COAST) * Math.min(1, Math.abs(velocity) / FLICK);
  const to = clampIndex(Math.round(pos.value + velocity / rate));
  go(to);
  settle(to, rate);
}
function onPointerCancel() {
  if (!drag) return;
  drag = null;
  const to = clampIndex(Math.round(pos.value));
  go(to);
  settle(to);
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
  .glow { transition: none; }
}
</style>
