<template>
  <div>
    <section id="shelf" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-7xl px-4 md:mt-16 md:px-8" aria-labelledby="shelf-title">
      <SectionHead title="Completed shelf" :subtitle="shelfSubtitle" />

      <Skeleton v-if="loading" variant="tiles" :count="4" />

      <p v-else-if="error" class="py-6 text-slate-400">
        {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
      </p>

      <template v-else-if="data">
        <ul v-if="data.completed.length" class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-x-3 gap-y-5 md:grid-cols-[repeat(auto-fill,minmax(148px,1fr))] md:gap-x-[18px] md:gap-y-6">
          <SeriesTile v-for="run in data.completed" :key="run.series.id" :series="run.series">
            <span class="text-xs font-semibold text-slate-400">{{ formatMonth(run.completed_at) }}</span>
            <span class="chip self-start" :class="STATUS_CHIP[run.status]">{{ STATUS_TEXT[run.status] }}</span>
          </SeriesTile>
        </ul>
        <p v-else class="py-4 text-slate-400">
          No complete runs yet.
          <a href="#get-next" class="font-bold text-sky-400 hover:text-sky-300">Get next shows what's closest</a>
        </p>
        <p v-if="data.single_volumes.count" class="mt-3.5 text-[13px] font-semibold text-slate-400">
          {{ data.single_volumes.count }} single volumes · {{ data.single_volumes.read }} read.
          <RouterLink to="/collection" class="font-bold text-sky-400 hover:text-sky-300">Open collection</RouterLink>
        </p>
      </template>
    </section>

    <section v-if="loading || (data && recordTiles.length)" id="records" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-7xl px-4 md:mt-16 md:px-8" aria-labelledby="records-title">
      <SectionHead title="Records" />
      <Skeleton v-if="loading" variant="figures" :count="5" />
      <div v-else class="grid grid-cols-2 gap-5 md:grid-cols-5">
        <StatFigure v-for="tile in recordTiles" :key="tile.label" :label="tile.label" :value="tile.value" :detail="tile.detail" compact />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import { daysSince, formatDate, formatMonth } from "@/utils/relativeTime";
import SectionHead from "./SectionHead.vue";
import SeriesTile from "./SeriesTile.vue";
import StatFigure from "./StatFigure.vue";
import Skeleton from "./Skeleton.vue";
import type { CompletedStatus, RecordEvent } from "@/types/insights.types";

const { data, loading, error, reload } = useInsightsSection(() => InsightsService.getRecords());

const STATUS_TEXT: Record<CompletedStatus, string> = { both: "Collected & read", collected: "Collected", read: "Read" };
const STATUS_CHIP: Record<CompletedStatus, string> = {
  both: "border-green-400/40 text-green-400",
  collected: "border-sky-400/40 text-sky-300",
  read: "border-green-400/40 text-green-400",
};

const shelfSubtitle = computed(() => {
  if (!data.value) return "";
  const runs = data.value.completed.length;
  const read = data.value.completed.filter((c) => c.status !== "collected").length;
  return runs ? `${runs} run${runs === 1 ? "" : "s"} · ${read} read to the end` : "";
});

const eventLabel = (e: RecordEvent) => (e.series.is_run ? `${e.series.display_title} #${e.issue.number}` : e.series.display_title);

const recordTiles = computed(() => {
  if (!data.value) return [];
  const { firsts, records } = data.value;
  const tiles: { label: string; value: string; detail: string }[] = [];
  if (firsts.first_read) tiles.push({ label: "First read", value: formatMonth(firsts.first_read.date), detail: eventLabel(firsts.first_read) });
  if (firsts.first_purchase) tiles.push({ label: "First purchase", value: formatMonth(firsts.first_purchase.date), detail: eventLabel(firsts.first_purchase) });
  if (records.biggest_buying_month) tiles.push({ label: "Biggest buying month", value: records.biggest_buying_month.label, detail: `${records.biggest_buying_month.count} books` });
  if (records.biggest_reading_month) tiles.push({ label: "Biggest reading month", value: records.biggest_reading_month.label, detail: `${records.biggest_reading_month.count} books` });
  if (records.longest_complete_run) tiles.push({ label: "Longest complete run", value: records.longest_complete_run.series.display_title, detail: `${records.longest_complete_run.issue_count} issues` });
  if (firsts.on_vertigo_since) tiles.push({ label: "On Vertigo since", value: formatDate(firsts.on_vertigo_since), detail: `${daysSince(firsts.on_vertigo_since)} days` });
  return tiles;
});
</script>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 9px;
  border-radius: 999px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
</style>
