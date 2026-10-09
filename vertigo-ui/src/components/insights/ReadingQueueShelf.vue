<template>
  <section id="pending" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-page px-4 md:mt-16 md:px-8" aria-labelledby="pending-title">
    <SectionHead title="Reading queue" :subtitle="subtitle" />

    <Skeleton v-if="loading" variant="tiles" :count="8" />

    <p v-else-if="error" class="py-6 text-slate-400">
      {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
    </p>

    <template v-else-if="items.length">
      <ul class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-x-3 gap-y-5 md:grid-cols-[repeat(auto-fill,minmax(148px,1fr))] md:gap-x-[18px] md:gap-y-6" :class="{ 'opacity-50': refreshing }">
        <SeriesTile v-for="item in visible" :key="item.series.id" :series="item.series">
          <RunStrip :run="item.run" />
          <span class="truncate text-xs font-semibold text-slate-400" :title="progressLine(item)">{{ progressLine(item) }}</span>
          <span class="truncate text-xs font-semibold text-slate-400" :title="statusLine(item)">{{ statusLine(item) }}</span>
        </SeriesTile>
      </ul>
      <div v-if="items.length > LIMIT" class="mt-4">
        <button class="text-sm font-bold text-sky-400 hover:text-sky-300" type="button" :aria-expanded="expanded" @click="expanded = !expanded">
          {{ expanded ? "Show fewer" : `Show all ${items.length}` }}
        </button>
      </div>
    </template>

    <p v-else class="py-6 text-slate-400">
      Everything you own is read.
      <a href="#get-next" class="font-bold text-sky-400 hover:text-sky-300">See what to get next</a>
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import { daysSince, formatMonth, relativeTime } from "@/utils/relativeTime";
import SectionHead from "./SectionHead.vue";
import SeriesTile from "./SeriesTile.vue";
import RunStrip from "./RunStrip.vue";
import Skeleton from "./Skeleton.vue";
import type { ReadingQueueItem } from "@/types/insights.types";

const LIMIT = 8;
const { data, loading, refreshing, error, reload } = useInsightsSection(() => InsightsService.getReadingQueue());
const expanded = ref(false);

const items = computed(() => data.value?.items ?? []);
const visible = computed(() => (expanded.value ? items.value : items.value.slice(0, LIMIT)));

const subtitle = computed(() => {
  if (!data.value) return "";
  const { total_unread, series_count } = data.value;
  return `${total_unread} unread across ${series_count} series`;
});

/** What to read and how far along: "#2 next · 1 of 2 read", or "Single volume". */
function progressLine(item: ReadingQueueItem): string {
  if (!item.series.is_run) return "Single volume";
  return `#${item.next_issue.number} next · ${item.series.read_count} of ${item.series.issue_count} read`;
}

/** One dated sentence in place of a status chip; the date says how fresh or stale it is. */
function statusLine(item: ReadingQueueItem): string {
  switch (item.marker) {
    case "fresh":
      return `Bought ${relativeTime(daysSince(item.marker_date))}`;
    case "stalled":
      return `Last read ${relativeTime(daysSince(item.marker_date))}`;
    case "not_started":
      return item.marker_date ? `Unread since ${formatMonth(item.marker_date)}` : "Unread";
    default:
      return item.last_read_at ? `Last read ${relativeTime(daysSince(item.last_read_at))}` : "";
  }
}
</script>


