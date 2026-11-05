<template>
  <div class="longbox">
    <LongboxStage class="longbox__stage" :items="items" :current="current" :pending="pending" :glow="glow" @update:current="current = $event" @open="open" />
    <LongboxScrubber v-if="items.length > 1" class="longbox__scrub" :items="items" :current="current" @update:current="current = $event" />
    <LongboxDetail class="longbox__detail" :item="items[settled] ?? null" :delete-mode="deleteMode" @confirm-delete="(id, title) => $emit('confirmDelete', id, title)" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import type { Series } from "@/types/series.types";
import { buildLongboxItems } from "./dividers";
import { dominantRgb } from "./color";
import LongboxStage from "./LongboxStage.vue";
import LongboxDetail from "./LongboxDetail.vue";
import LongboxScrubber from "./LongboxScrubber.vue";

const props = withDefaults(defineProps<{ seriesList: Series[]; orderBy: string; deleteMode: boolean; pending?: number; resultsKey?: number }>(), {
  pending: 0,
  resultsKey: 0,
});
defineEmits<{ (e: "confirmDelete", id: number, title: string): void }>();

/** How long the row has to be still before the panel and the glow follow it. */
const SETTLE_MS = 140;

const router = useRouter();
const items = computed(() => buildLongboxItems(props.seriesList, props.orderBy));
const current = ref(0);

// The row answers every step at once; the panel and the glow wait for it to come to rest, so a
// flick through twenty covers does not rebuild the panel twenty times on the way.
const settled = ref(0);
let settleTimer: ReturnType<typeof setTimeout> | null = null;
watch(current, (index) => {
  if (settleTimer) clearTimeout(settleTimer);
  settleTimer = setTimeout(() => { settled.value = index; settleTimer = null; }, SETTLE_MS);
});
onBeforeUnmount(() => { if (settleTimer) clearTimeout(settleTimer); });

// the ambient light takes the colour of the cover in front; dividers leave it neutral
const glow = computed(() => {
  const item = items.value[settled.value];
  return item?.kind === "series" ? dominantRgb(item.series.dominant_color) : null;
});

const firstSeries = () => Math.max(0, items.value.findIndex((item) => item.kind === "series"));

// Every fresh fetch (a new search, sort or filter) bumps resultsKey and starts the box over at
// the first cover; pages appended to the same fetch leave the row where the reader left it.
watch(() => props.resultsKey, () => {
  current.value = firstSeries();
  settled.value = current.value;
}, { immediate: true });
watch(() => items.value.length, (length) => {
  if (current.value > length - 1) current.value = Math.max(0, length - 1);
  if (settled.value > length - 1) settled.value = Math.max(0, length - 1);
});

function open(series: Series) {
  router.push({ name: "SeriesDetail", params: { Link: series.slug, Id: series.id } });
}
</script>

<style scoped>
/*
 * Phone first: the covers, the scrubber right under them, then the panel. From tablet width the
 * panel moves beside the stage and the scrubber runs under both. Stage and panel share --lb-h,
 * which leaves room for the header, toolbar and scrubber so the box fits the window.
 */
.longbox {
  --lb-h: 340px;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  grid-template-areas: "stage" "scrub" "detail";
  column-gap: 28px;
}
.longbox__stage { grid-area: stage; }
.longbox__scrub { grid-area: scrub; }
.longbox__detail { grid-area: detail; margin-top: 20px; }
@media (min-width: 768px) {
  .longbox {
    --lb-h: clamp(380px, calc(100vh - 340px), 480px);
    grid-template-columns: minmax(0, 1fr) 300px;
    grid-template-areas: "stage detail" "scrub scrub";
  }
  .longbox__detail { margin-top: 0; }
}
@media (min-width: 1024px) {
  .longbox { grid-template-columns: minmax(0, 1fr) 360px; }
}
</style>
