<template>
  <div class="room">
    <div ref="stage" class="room__stage" :class="{ 'room__stage--hot': !!hovered }"></div>

    <div class="room__title">
      <h1>Reading room</h1>
      <p>{{ subtitle }}</p>
    </div>

    <p class="room__hint">Scroll to lean in · click a comic to pick it up · <kbd>Esc</kbd> puts it back</p>

    <Transition name="card">
      <aside v-if="picked" class="room__card">
        <h2>{{ picked.title }}</h2>
        <p class="room__meta">{{ [picked.publisher, picked.format, picked.year].filter(Boolean).join(" · ") }}</p>
        <div class="bars">
          <div class="bar">Owned <span class="num">{{ picked.owned }} of {{ picked.issues }}</span><i><b class="bar__owned" :style="{ width: share(picked.owned, picked.issues) }"></b></i></div>
          <div class="bar">Read <span class="num">{{ picked.read }} of {{ picked.issues }}</span><i><b class="bar__read" :style="{ width: share(picked.read, picked.issues) }"></b></i></div>
        </div>
        <div class="tags">
          <span v-for="tag in [...picked.genre, ...picked.creators.slice(0, 3)]" :key="tag">{{ tag }}</span>
          <span v-if="picked.rating">{{ "★".repeat(Math.round(picked.rating)) }}</span>
        </div>
        <RouterLink :to="{ name: 'SeriesDetail', params: { Link: picked.slug, Id: picked.id } }" class="btn">Open series</RouterLink>
        <button type="button" class="link" @click="putBack">Put it back</button>
      </aside>
    </Transition>

    <div v-if="loading" class="room__state">
      <b class="num">{{ percent }}</b>
      <span>{{ seriesCount ? "Hanging your covers" : "Fetching the collection" }}</span>
    </div>
    <div v-else-if="failed" class="room__state room__state--text">
      <b>{{ failed }}</b>
      <span>The rest of the app still works; try again in a moment.</span>
    </div>
    <div v-else-if="!seriesCount" class="room__state room__state--text">
      <b>The shelves are empty.</b>
      <span>Add a few series and they will stand here, face out.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { loadRoomSeries, type RoomSeries } from "@/components/reading-room/roomData";
import { createRoom, type RoomHandle } from "@/components/reading-room/roomScene";

const stage = ref<HTMLElement | null>(null);
const loading = ref(true);
const failed = ref("");
const percent = ref(0);
const seriesCount = ref(0);
const total = ref(0);
const issues = ref(0);
const picked = ref<RoomSeries | null>(null);
const hovered = ref<RoomSeries | null>(null);
let room: RoomHandle | null = null;

const subtitle = computed(() => {
  if (!seriesCount.value) return "A quiet place for the collection.";
  const shown = total.value > seriesCount.value ? `${seriesCount.value} of ${total.value} series` : `${seriesCount.value} series`;
  return `${shown} · ${issues.value} issues`;
});
const share = (count: number, all: number) => `${all ? Math.min(100, (count / all) * 100) : 0}%`;

function putBack() {
  room?.putBack();
}
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") putBack();
}

onMounted(async () => {
  document.addEventListener("keydown", onKey);
  let series: RoomSeries[];
  try {
    const result = await loadRoomSeries();
    series = result.series;
    total.value = result.total;
  } catch (error) {
    console.error("Failed to load the reading room", error);
    failed.value = "The collection could not be loaded.";
    loading.value = false;
    return;
  }
  seriesCount.value = series.length;
  issues.value = series.reduce((sum, s) => sum + s.owned, 0);
  if (!series.length || !stage.value) {
    loading.value = false;
    return;
  }
  try {
    room = createRoom(stage.value, series, {
      onProgress: (loaded, all) => {
        percent.value = Math.min(100, Math.round((loaded / all) * 100));
        if (percent.value >= 60) loading.value = false;
      },
      onPick: (s) => { picked.value = s; },
      onHover: (s) => { hovered.value = s; },
    });
    // a slow network still gets the room; the covers keep arriving behind it
    setTimeout(() => { loading.value = false; }, 6000);
  } catch (error) {
    console.error("The reading room could not start", error);
    failed.value = "Your browser could not start the 3D room.";
    loading.value = false;
  }
});
onBeforeUnmount(() => {
  document.removeEventListener("keydown", onKey);
  room?.dispose();
  room = null;
});
</script>

<style scoped>
/* The room is one screen under the header. Everything else floats over the canvas. */
.room {
  position: relative;
  height: calc(100vh - var(--spacing-header, 72px));
  overflow: hidden;
  background: #0a0b10;
}
.room__stage { position: absolute; inset: 0; }
.room__stage--hot { cursor: pointer; }
.room__stage :deep(canvas) { display: block; }
/* a soft vignette and a little grain over the render; both are stills, so they cost nothing per frame */
.room::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: radial-gradient(125% 95% at 50% 45%, transparent 55%, rgba(0, 0, 0, 0.45) 100%);
}
.room::after {
  content: "";
  position: absolute;
  inset: -50%;
  z-index: 2;
  pointer-events: none;
  opacity: 0.045;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  animation: grain 1.2s steps(6) infinite;
}
@keyframes grain {
  0% { transform: translate(0, 0); }
  20% { transform: translate(-3%, 2%); }
  40% { transform: translate(2%, -4%); }
  60% { transform: translate(-4%, -1%); }
  80% { transform: translate(3%, 3%); }
  100% { transform: translate(0, 0); }
}

.room__title { position: absolute; left: 32px; top: 24px; z-index: 3; pointer-events: none; }
.room__title h1 { margin: 0; font-size: clamp(26px, 3.2vw, 38px); font-weight: 900; line-height: 1; letter-spacing: -0.03em; color: #fff; text-shadow: 0 8px 30px rgba(0, 0, 0, 0.6); }
.room__title p { margin: 8px 0 0; font-size: 13px; font-weight: 700; color: #94a3b8; }

.room__hint { position: absolute; left: 32px; bottom: 20px; z-index: 3; margin: 0; font-size: 12px; font-weight: 700; color: #64748b; pointer-events: none; }
.room__hint kbd { display: inline-block; min-width: 20px; padding: 0 5px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.12); font: inherit; font-size: 11px; line-height: 18px; text-align: center; color: #94a3b8; }

.room__card { position: absolute; right: 32px; top: 50%; z-index: 4; width: min(340px, calc(100% - 64px)); transform: translateY(-50%); }
.room__card h2 { margin: 0; font-size: 28px; font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; color: #fff; text-shadow: 0 8px 30px rgba(0, 0, 0, 0.6); }
.room__meta { margin: 8px 0 0; font-size: 13px; font-weight: 700; color: #94a3b8; }
.bars { display: flex; flex-direction: column; gap: 10px; margin-top: 18px; }
.bar { font-size: 12px; font-weight: 800; color: #cbd5e1; }
.bar span { float: right; color: #94a3b8; }
.bar i { display: block; height: 5px; margin-top: 6px; border-radius: 999px; background: rgba(255, 255, 255, 0.1); overflow: hidden; }
.bar b { display: block; height: 100%; border-radius: 999px; }
.bar__owned { background: #0ea5e9; }
.bar__read { background: #4ade80; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }
.tags span { padding: 3px 9px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(6, 8, 15, 0.5); font-size: 11px; font-weight: 800; color: #cbd5e1; }
.btn { display: inline-flex; align-items: center; height: 36px; margin-top: 20px; padding: 0 14px; border-radius: 5px; background: #fff; color: #0f172a; font-size: 13px; font-weight: 800; }
.btn:hover { background: #ffe9cf; }
.link { display: block; margin-top: 10px; font-size: 12px; font-weight: 800; color: #94a3b8; }
.link:hover { color: #fff; }
.card-enter-active { transition: opacity 0.35s, transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1); }
.card-leave-active { transition: opacity 0.2s; }
.card-enter-from { opacity: 0; transform: translateY(-50%) translateX(24px); }
.card-leave-to { opacity: 0; }

.room__state { position: absolute; inset: 0; z-index: 5; display: grid; place-content: center; text-align: center; background: #0a0b10; }
.room__state b { display: block; font-size: clamp(48px, 10vw, 120px); font-weight: 900; line-height: 1; letter-spacing: -0.04em; color: #fff; }
.room__state span { display: block; margin-top: 10px; font-size: 13px; font-weight: 700; color: #94a3b8; }
.room__state--text b { max-width: 420px; font-size: 20px; letter-spacing: -0.01em; }
.num { font-variant-numeric: tabular-nums; }

@media (max-width: 767px) {
  .room__title { left: 16px; top: 16px; }
  .room__hint { display: none; }
  .room__card { right: 16px; left: 16px; top: auto; bottom: 16px; width: auto; transform: none; }
  .card-enter-from { transform: translateY(24px); }
}
@media (prefers-reduced-motion: reduce) {
  .room::after { animation: none; }
  .card-enter-active, .card-leave-active { transition: none; }
}
</style>
