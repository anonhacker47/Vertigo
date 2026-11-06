<template>
  <div class="room">
    <div ref="stage" class="room__stage" :class="{ 'room__stage--hot': !!hovered, 'room__stage--on': !loading }"></div>

    <div class="room__title">
      <h1>Reading room</h1>
      <p>{{ subtitle }}</p>
    </div>

    <p v-show="!secretOpen" class="room__hint">Scroll to lean in · click a comic to pick it up · <kbd>Esc</kbd> puts it back · click a lamp to switch it · <kbd>P</kbd> takes a shelfie<template v-if="pages > 1"> · <kbd>←</kbd> <kbd>→</kbd> turn the shelf</template></p>

    <Transition name="fade">
      <button v-if="!holding && !secretOpen && !loading" type="button" class="room__shutter" aria-label="Take a shelfie" title="Take a shelfie (P)" @click="shelfie"><i class="pi pi-camera"></i></button>
    </Transition>
    <Transition name="snap"><div v-if="flash" class="room__flash"></div></Transition>

    <Transition name="card">
      <aside v-if="photo" class="room__card">
        <h2>Shelfie</h2>
        <p class="room__meta">{{ photo.taken.toLocaleString() }}</p>
        <a :href="photo.jpeg" :download="`shelfie-${stamp(photo.taken)}.jpg`" class="btn">Download photo</a>
        <button type="button" class="link" @click="room?.removePhoto(photo.id)">Take it down</button>
        <button type="button" class="link" @click="putBack">Pin it back</button>
      </aside>
    </Transition>

    <Transition name="fade">
      <div v-if="pages > 1 && !holding && !secretOpen" class="room__pager" role="group" aria-label="Shelf pages" :style="{ left: `${shelfFoot.x * 100}%`, top: `${shelfFoot.y * 100}%` }">
        <button type="button" :disabled="busy" aria-label="Previous shelf" @click="turn(-1)">‹</button>
        <span>Shelf <b class="num">{{ page + 1 }}</b> of <b class="num">{{ pages }}</b></span>
        <button type="button" :disabled="busy" aria-label="Next shelf" @click="turn(1)">›</button>
      </div>
    </Transition>

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

    <Transition name="veil">
      <div v-if="loading" class="room__state">
        <i class="veil__glow"></i>
        <p class="veil__kicker">Reading room</p>
        <b class="num">{{ Math.round(shown) }}</b>
        <div class="veil__bar"><i :style="{ width: `${shown}%` }"></i></div>
        <span>{{ caption }}</span>
      </div>
    </Transition>
    <div v-if="!loading && failed" class="room__state room__state--text">
      <b>{{ failed }}</b>
      <span>The rest of the app still works; try again in a moment.</span>
    </div>
    <div v-if="!loading && !failed && !seriesCount" class="room__state room__state--text">
      <b>The shelves are empty.</b>
      <span>Add a few series and they will stand here, face out.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { loadRoomSeries, loadRoomSummary, type RoomSeries } from "@/components/reading-room/roomData";
import { createRoom, type RoomHandle, type RoomPhoto } from "@/components/reading-room/roomScene";

const stage = ref<HTMLElement | null>(null);
const loading = ref(true);
const failed = ref("");
const shown = ref(0); // the number on the veil eases toward the real progress, then runs to a hundred
let target = 6;
let veilFrame = 0;
const seriesCount = ref(0);
const total = ref(0);
const issues = ref(0);
const picked = ref<RoomSeries | null>(null);
const hovered = ref<RoomSeries | null>(null);
const page = ref(0);
const pages = ref(1);
const busy = ref(false);
const shelfFoot = ref({ x: 0.28, y: 0.78 });
const holding = ref(false);
const secretOpen = ref(false);
const photo = ref<RoomPhoto | null>(null);
const flash = ref(false);
let room: RoomHandle | null = null;

const subtitle = computed(() => {
  if (!seriesCount.value) return "A quiet place for the collection.";
  const shown = total.value > seriesCount.value ? `${seriesCount.value} of ${total.value} series` : `${seriesCount.value} series`;
  return `${shown} · ${issues.value} issues`;
});
const caption = computed(() => (shown.value < 25 ? "Fetching the collection" : shown.value < 75 ? "Hanging your covers" : "Lighting the lamps"));
function easeVeil() {
  shown.value += (target - shown.value) * 0.07;
  if (target >= 100 && shown.value > 99.4) { shown.value = 100; loading.value = false; return; }
  veilFrame = requestAnimationFrame(easeVeil);
}
const share = (count: number, all: number) => `${all ? Math.min(100, (count / all) * 100) : 0}%`;

function putBack() {
  room?.putBack();
}
const stamp = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
function shelfie() {
  if (!room || holding.value || secretOpen.value) return;
  flash.value = true;
  setTimeout(() => { flash.value = false; }, 160);
  room.takeShelfie();
}
function turn(step: number) {
  room?.showPage(page.value + step);
}
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") putBack();
  else if (event.key === "ArrowLeft") turn(-1);
  else if (event.key === "ArrowRight") turn(1);
  else if (event.key === "p" || event.key === "P") shelfie();
}

onMounted(async () => {
  document.addEventListener("keydown", onKey);
  easeVeil();
  let series: RoomSeries[];
  try {
    const result = await loadRoomSeries();
    series = result.series;
    total.value = result.total;
    target = Math.max(target, 18);
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
        const done = Math.min(100, (loaded / all) * 100);
        target = done >= 60 ? 100 : Math.max(target, done); // from sixty the rest arrives behind the room
      },
      onPick: (s) => { picked.value = s; },
      onHover: (s) => { hovered.value = s; },
      onPage: (current, all, turning) => { page.value = current; pages.value = all; busy.value = turning; },
      onLayout: (foot) => { shelfFoot.value = foot; },
      onHold: (held) => { holding.value = held; },
      onSecret: (open) => { secretOpen.value = open; },
      onPhoto: (p) => { photo.value = p; },
    });
    // a slow network still gets the room; the covers keep arriving behind it
    setTimeout(() => { target = 100; }, 6000);
    loadRoomSummary({ series: total.value, issues: issues.value }).then((summary) => room?.setSummary(summary)).catch(() => {});
  } catch (error) {
    console.error("The reading room could not start", error);
    failed.value = "Your browser could not start the 3D room.";
    loading.value = false;
  }
});
onBeforeUnmount(() => {
  cancelAnimationFrame(veilFrame);
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
.room__stage { position: absolute; inset: 0; opacity: 0; transition: opacity 1.6s ease; }
.room__stage--on { opacity: 1; }
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

.room__shutter { position: absolute; right: 32px; bottom: 18px; z-index: 3; display: grid; place-items: center; width: 40px; height: 40px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, 0.14); background: rgba(10, 11, 16, 0.55); color: #e2e8f0; font-size: 16px; }
.room__shutter:hover { color: #fff; background: rgba(255, 255, 255, 0.12); }
.room__flash { position: absolute; inset: 0; z-index: 6; background: #fff; pointer-events: none; }
.snap-enter-active { transition: opacity 0.04s; }
.snap-leave-active { transition: opacity 0.3s ease-out; }
.snap-enter-from, .snap-leave-to { opacity: 0; }

/* sits just under the bookcase; the scene says where that is on screen */
.room__pager { position: absolute; z-index: 3; transform: translate(-50%, 12px); display: inline-flex; align-items: center; gap: 6px; padding: 3px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(10, 11, 16, 0.55); }
.room__pager span { padding: 0 6px; font-size: 12px; font-weight: 700; color: #94a3b8; }
.room__pager b { color: #fff; }
.room__pager button { width: 28px; height: 28px; border-radius: 999px; font-size: 18px; line-height: 1; color: #cbd5e1; }
.room__pager button:hover:not(:disabled) { color: #fff; background: rgba(255, 255, 255, 0.12); }
.room__pager button:disabled { opacity: 0.4; }

/* a small frosted card: the room shows through it, blurred */
.room__card {
  position: absolute; right: 32px; top: 50%; z-index: 4;
  width: min(320px, calc(100% - 64px));
  padding: 20px 22px 22px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(12, 14, 22, 0.42);
  -webkit-backdrop-filter: blur(18px) saturate(1.3);
  backdrop-filter: blur(18px) saturate(1.3);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transform: translateY(-50%);
}
.room__card h2 { margin: 0; font-size: 26px; font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; color: #fff; }
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
.fade-enter-active { transition: opacity 0.3s 0.15s; }
.fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.room__state { position: absolute; inset: 0; z-index: 5; display: grid; place-content: center; justify-items: center; text-align: center; background: #0a0b10; overflow: hidden; }
.veil__glow { position: absolute; left: 50%; top: 50%; width: 70vmin; height: 70vmin; border-radius: 50%; background: radial-gradient(circle, rgba(255, 196, 120, 0.16), rgba(255, 196, 120, 0) 70%); animation: breathe 3.2s ease-in-out infinite; pointer-events: none; }
@keyframes breathe { 0%, 100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.7; } 50% { transform: translate(-50%, -50%) scale(1.08); opacity: 1; } }
.veil__kicker { position: relative; margin: 0 0 14px; font-size: 12px; font-weight: 800; letter-spacing: 0.28em; text-transform: uppercase; color: #a8906a; }
.room__state b { position: relative; display: block; font-size: clamp(64px, 12vw, 150px); font-weight: 900; line-height: 1; letter-spacing: -0.04em; color: #fff; }
.veil__bar { position: relative; width: min(260px, 60vw); height: 2px; margin: 22px auto 0; border-radius: 2px; background: rgba(255, 255, 255, 0.1); overflow: hidden; }
.veil__bar i { display: block; height: 100%; background: linear-gradient(90deg, #d9b86a, #f3e6b8); }
.room__state span { position: relative; display: block; margin-top: 14px; font-size: 13px; font-weight: 700; color: #94a3b8; }
.veil-leave-active { transition: opacity 1s ease; }
.veil-leave-to { opacity: 0; }
.room__state--text b { max-width: 420px; font-size: 20px; letter-spacing: -0.01em; }
.num { font-variant-numeric: tabular-nums; }

@media (max-width: 767px) {
  .room__title { left: 16px; top: 16px; }
  .room__hint { display: none; }
  .room__shutter { right: 16px; bottom: 16px; }
  .room__card { right: 16px; left: 16px; top: auto; bottom: 16px; width: auto; padding: 16px 18px 18px; transform: none; }
  .card-enter-from { transform: translateY(24px); }
}
@media (prefers-reduced-motion: reduce) {
  .room::after, .veil__glow { animation: none; }
  .card-enter-active, .card-leave-active, .fade-enter-active, .fade-leave-active { transition: none; }
}
</style>
