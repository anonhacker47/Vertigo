<template>
  <section
    id="up-next"
    class="scroll-mt-[calc(var(--spacing-header)+1rem)] relative -mt-header overflow-hidden pt-[calc(var(--spacing-header)+2.5rem)] pb-10 md:pt-[calc(var(--spacing-header)+4rem)] md:pb-16"
    aria-labelledby="up-next-title"
    @keydown.left.prevent="step(-1)"
    @keydown.right.prevent="step(1)"
  >
    <Transition name="wash">
      <div v-if="front" :key="front.issue.id" class="ins-wash" aria-hidden="true" :style="{ background: placeholderGradient(front.series.title) }">
        <img v-if="washFailedId !== front.issue.id" :src="front.issue.cover" alt="" @error="washFailedId = front.issue.id" />
      </div>
    </Transition>
    <div class="ins-scrim" aria-hidden="true"></div>

    <div class="relative mx-auto w-full max-w-7xl px-4 md:px-8">
      <Skeleton v-if="loading" variant="hero" />

      <div v-else-if="error" class="py-6 text-slate-400">
        {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
      </div>

      <div v-else-if="front" class="grid items-center gap-7 md:grid-cols-[7fr_5fr] md:gap-10">
        <Transition name="xfade" mode="out-in">
          <div :key="front.issue.id">
            <p class="text-[13px] font-bold text-slate-400">To be read</p>
            <h1 id="up-next-title" class="mt-2 text-[28px] font-extrabold leading-tight text-white md:text-[40px]" style="text-wrap: balance">
              {{ front.series.display_title }}<span v-if="front.series.is_run" class="ml-2 font-bold text-slate-400">#{{ front.issue.number }}</span>
            </h1>
            <p class="mt-2.5 text-sm font-semibold text-slate-400">{{ metaFor(front) }}</p>
            <p class="mt-5 max-w-[34ch] text-lg font-semibold text-slate-300" style="text-wrap: pretty">{{ front.reason }}</p>
            <div class="mt-6 flex flex-wrap items-center gap-5">
              <RouterLink :to="issueRoute(front)" class="btn btn-border">Open issue</RouterLink>
              <a href="#pending" class="font-bold text-sky-400 hover:text-sky-300">See all pending</a>
            </div>
            <p v-if="entries.length > 1" class="mt-5 text-sm font-semibold text-slate-400">
              {{ frontIndex === 0 ? "Also on deck:" : "Back to:" }}
              <template v-for="(entry, i) in others" :key="entry.issue.id">
                <span v-if="i > 0"> · </span>
                <button type="button" class="border-b border-slate-600 text-slate-300 hover:border-sky-400 hover:text-sky-300" @click="bringForward(entry)">{{ entry.label }}</button>
              </template>
            </p>
          </div>
        </Transition>

        <div class="deck" :class="{ 'deck--single': entries.length === 1 }" role="group" aria-label="Up next and on deck. Use the arrow keys to flip.">
          <div v-for="(entry, i) in entries" :key="entry.issue.id" class="deck__slot" :class="`deck__slot--${slotOf(i)}`">
            <RouterLink v-if="slotOf(i) === 0" :to="issueRoute(entry)" class="block h-full w-full" :aria-label="entry.label">
              <CoverImage :src="entry.issue.cover" :title="entry.series.title" :alt="entry.label" :aspect="false" depth="lg" initials-class="text-6xl" class="h-full w-full" />
            </RouterLink>
            <button v-else type="button" class="block h-full w-full" :aria-label="`Bring ${entry.label} to the front`" @click="bringForward(entry)">
              <CoverImage :src="entry.issue.cover" :title="entry.series.title" :alt="entry.label" :aspect="false" depth="lg" :interactive="false" initials-class="text-6xl" class="h-full w-full" />
            </button>
          </div>
        </div>
      </div>

      <div v-else class="max-w-2xl py-4">
        <p class="text-[13px] font-bold text-slate-400">Up next</p>
        <h1 id="up-next-title" class="mt-2 text-[28px] font-extrabold leading-tight text-white md:text-[40px]">{{ empty.title }}</h1>
        <p class="mt-4 max-w-[48ch] text-lg font-semibold text-slate-300">{{ empty.line }}</p>
        <div class="mt-6"><RouterLink :to="empty.to" class="btn-cta">{{ empty.cta }}</RouterLink></div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import { placeholderGradient } from "@/utils/placeholderGradient";
import CoverImage from "@/components/common/CoverImage.vue";
import Skeleton from "./Skeleton.vue";
import type { UpNextEntry } from "@/types/insights.types";

const { data, loading, error, reload } = useInsightsSection(() => InsightsService.getUpNext());
const washFailedId = ref<number | null>(null);

const entries = computed<UpNextEntry[]>(() => (data.value?.hero ? [data.value.hero, ...data.value.on_deck] : []));
const frontIndex = ref(0);
watch(entries, () => { frontIndex.value = 0; });

const front = computed(() => entries.value[frontIndex.value] ?? null);
const others = computed(() => entries.value.filter((_, i) => i !== frontIndex.value));

function slotOf(i: number): number {
  const n = entries.value.length;
  return n ? (i - frontIndex.value + n) % n : 0;
}
function bringForward(entry: UpNextEntry) {
  const i = entries.value.findIndex((e) => e.issue.id === entry.issue.id);
  if (i >= 0) frontIndex.value = i;
}
function step(delta: number) {
  const n = entries.value.length;
  if (n > 1) frontIndex.value = (frontIndex.value + delta + n) % n;
}

function metaFor(entry: UpNextEntry): string {
  const s = entry.series;
  const parts = [s.manga ? "Manga" : s.series_format, s.publisher].filter(Boolean) as string[];
  if (s.is_run) {
    parts.push(`${s.read_count} of ${s.issue_count} read`);
    const waiting = s.owned_count - s.read_count;
    if (waiting > 0) parts.push(`${waiting} on the shelf`);
  }
  return parts.join(" · ");
}

const empty = computed(() => {
  switch (data.value?.state) {
    case "nothing_owned":
      return { title: "Nothing marked as owned.", line: "Open a series and mark the issues you have. Everything here builds from ownership.", cta: "Open collection", to: "/collection" };
    case "nothing_unread":
      return { title: "Nothing unread on the shelf.", line: "Everything you own, you've read. Get next shows which run is closest to complete.", cta: "Open collection", to: "/collection" };
    default:
      return { title: "Your desk is empty.", line: "Add a series and mark what you own. Insights fills in from there: what to read next, what to buy next, how the shelf is growing.", cta: "Add series", to: "/series/create" };
  }
});


function issueRoute(entry: UpNextEntry) {
  return { name: "IssueDetail", params: { seriesId: entry.series.id, slug: entry.series.slug, number: entry.issue.number } };
}
</script>

<style scoped>
/* ---- wash: the front cover, blurred, drifting slowly ---- */
.ins-wash {
  position: absolute;
  inset: -20% -10% 0 -10%;
  pointer-events: none;
  opacity: 0.35;
  filter: blur(60px) saturate(1.15);
  -webkit-mask-image: linear-gradient(to bottom, #000 40%, transparent 100%);
  mask-image: linear-gradient(to bottom, #000 40%, transparent 100%);
}
.ins-wash img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.06);
}
/* keeps the transparent nav legible over a bright cover */
.ins-scrim {
  position: absolute;
  inset: 0 0 auto 0;
  height: calc(var(--spacing-header) * 1.5);
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0));
}
.wash-enter-active, .wash-leave-active { transition: opacity 0.7s ease; }
.wash-enter-from, .wash-leave-to { opacity: 0; }

/* ---- text block cross-fade when the deck flips ---- */
.xfade-enter-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.xfade-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.xfade-enter-from { opacity: 0; transform: translateY(8px); }
.xfade-leave-to { opacity: 0; transform: translateY(-6px); }

/* ---- the deck: front cover plus two fanned behind it ---- */
.deck {
  --cover-w: 176px;
  --cover-h: 264px;
  --fan-x: 22px;
  --fan-y: 12px;
  position: relative;
  justify-self: center;
  width: calc(var(--cover-w) + var(--fan-x) * 2 + 12px);
  height: calc(var(--cover-h) + var(--fan-y) * 2 + 34px);
}
.deck--single {
  width: calc(var(--cover-w) + 12px);
  height: calc(var(--cover-h) + 34px);
}
@media (min-width: 768px) {
  .deck {
    --cover-w: 280px;
    --cover-h: 420px;
    --fan-x: 34px;
    --fan-y: 18px;
    justify-self: end;
    margin-right: 8px;
  }
}
.deck__slot {
  position: absolute;
  left: 0;
  top: 0;
  width: var(--cover-w);
  height: var(--cover-h);
  transform-origin: bottom left;
}
.deck__slot--0 { z-index: 3; transform: translate(0, 0) rotate(0) scale(1); filter: none; }
.deck__slot--1 { z-index: 2; transform: translate(var(--fan-x), var(--fan-y)) rotate(3deg) scale(0.95); filter: brightness(0.7); }
.deck__slot--2 { z-index: 1; transform: translate(calc(var(--fan-x) * 2), calc(var(--fan-y) * 2)) rotate(6deg) scale(0.9); filter: brightness(0.5); }
.deck__slot--1:hover, .deck__slot--2:hover { filter: brightness(0.9); }
.deck__slot button { cursor: pointer; }

.shelf-line {
  position: absolute;
  left: 0;
  bottom: 0;
  width: calc(100% - 12px);
  height: 1px;
  background: #334155;
}

@media (prefers-reduced-motion: no-preference) {
  .deck__slot { transition: transform 0.45s cubic-bezier(0.2, 0.7, 0.2, 1), filter 0.45s ease; }
  .ins-wash img { animation: drift 14s ease-in-out infinite alternate; }
  @keyframes drift {
    from { transform: translate(0, 0) scale(1.06); }
    to { transform: translate(-3%, 2%) scale(1.14); }
  }
}
@media (prefers-reduced-motion: reduce) {
  .xfade-enter-active, .xfade-leave-active, .wash-enter-active, .wash-leave-active { transition: none; }
}
</style>
