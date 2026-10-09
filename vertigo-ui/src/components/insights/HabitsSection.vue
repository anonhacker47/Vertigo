<template>
  <section id="habits" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-page px-4 md:mt-16 md:px-8" aria-labelledby="habits-title">
    <SectionHead title="Habits">
      <div class="seg" role="group" aria-label="Range">
        <button v-for="r in RANGES" :key="r.key" type="button" :aria-pressed="range === r.key" @click="range = r.key">{{ r.label }}</button>
      </div>
    </SectionHead>

    <template v-if="loading">
      <Skeleton variant="figures" :count="4" />
      <div class="mt-6"><Skeleton variant="chart" /></div>
    </template>

    <p v-else-if="error" class="py-6 text-slate-400">
      {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
    </p>

    <template v-else-if="data">
      <div class="mb-6 grid grid-cols-2 gap-5 md:grid-cols-4">
        <StatFigure label="Unread on the shelf" :value="format(figures.unread.count)" :detail="`across ${figures.unread.series_count} series`" />
        <StatFigure v-if="figures.last_read" label="Last read" :value="capitalize(relativeTime(figures.last_read.days))">
          <RouterLink :to="issueRoute(figures.last_read)" class="border-b border-slate-600 hover:border-sky-400 hover:text-sky-300">{{ issueLabel(figures.last_read) }}</RouterLink>
        </StatFigure>
        <StatFigure v-if="figures.bought_to_read" label="Bought to read" :value="spanText(figures.bought_to_read.median_days)" :detail="`typical wait, over ${figures.bought_to_read.sample} books`" />
        <StatFigure v-if="figures.waiting_longest" label="Waiting longest" :value="spanText(figures.waiting_longest.days)">
          <RouterLink :to="issueRoute(figures.waiting_longest)" class="border-b border-slate-600 hover:border-sky-400 hover:text-sky-300">{{ issueLabel(figures.waiting_longest) }}</RouterLink>, since {{ formatMonth(figures.waiting_longest.since) }}
        </StatFigure>
      </div>

      <div :class="{ 'opacity-50': refreshing }">
        <ActivityChart v-if="hasAnyActivity" :buckets="data.buckets" :mode="data.mode" />
        <p v-else class="py-4 text-slate-400">
          No dates yet. Marking an issue as owned or read stamps today's date.
          <RouterLink to="/collection" class="font-bold text-sky-400 hover:text-sky-300">Open collection</RouterLink>
        </p>
        <p v-if="hasAnyActivity" class="mt-3 text-[15px] font-semibold text-slate-300">{{ sentence }}</p>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import { capitalize, formatMonth, relativeTime, spanText } from "@/utils/relativeTime";
import SectionHead from "./SectionHead.vue";
import StatFigure from "./StatFigure.vue";
import ActivityChart from "./ActivityChart.vue";
import Skeleton from "./Skeleton.vue";
import type { ActivityRange, DatedIssue } from "@/types/insights.types";

const RANGES: { key: ActivityRange; label: string }[] = [
  { key: "ytd", label: "This year" },
  { key: "last_year", label: "Last year" },
  { key: "all", label: "All time" },
];
const PERIOD: Record<ActivityRange, string> = { ytd: "so far this year", last_year: "last year", all: "all time" };

const range = ref<ActivityRange>("ytd");
const { data, loading, refreshing, error, reload } = useInsightsSection(() => InsightsService.getActivity(range.value));
watch(range, () => reload());

const figures = computed(() => data.value!.figures);
const hasAnyActivity = computed(() => (data.value?.buckets ?? []).some((b) => b.bought || b.read));

const sentence = computed(() => {
  if (!data.value) return "";
  const { bought, read } = data.value.totals;
  const diff = bought - read;
  const shelf = diff > 0 ? `The shelf grew by ${diff}.` : diff < 0 ? `The shelf shrank by ${-diff}.` : "The shelf held steady.";
  return `You bought ${bought} and read ${read} ${PERIOD[data.value.range]}. ${shelf}`;
});

const format = (n: number) => new Intl.NumberFormat().format(n);
const issueLabel = (d: DatedIssue) => (d.series.is_run ? `${d.series.display_title} #${d.issue.number}` : d.series.display_title);
const issueRoute = (d: DatedIssue) => ({ name: "IssueDetail", params: { seriesId: d.series.id, slug: d.series.slug, number: d.issue.number } });
</script>

<style scoped>
.seg {
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  border-radius: 10px;
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.seg button {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 700;
  color: #94a3b8;
  white-space: nowrap;
}
.seg button[aria-pressed="true"] {
  background: #1e293b;
  color: #fff;
}
</style>
