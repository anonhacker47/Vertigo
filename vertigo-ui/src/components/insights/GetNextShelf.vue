<template>
  <section id="get-next" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-page px-4 md:mt-16 md:px-8" aria-labelledby="get-next-title">
    <SectionHead title="Get next" :subtitle="subtitle">
      <div v-if="items.length > 1" class="seg" role="group" aria-label="Sort">
        <button type="button" :aria-pressed="sort === 'closest'" @click="sort = 'closest'">Closest to done</button>
        <button type="button" :aria-pressed="sort === 'recent'" @click="sort = 'recent'">Recently bought</button>
      </div>
    </SectionHead>

    <Skeleton v-if="loading" variant="tiles" :count="8" />

    <p v-else-if="error" class="py-6 text-slate-400">
      {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
    </p>

    <template v-else-if="items.length">
      <ul class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-x-3 gap-y-5 md:grid-cols-[repeat(auto-fill,minmax(148px,1fr))] md:gap-x-[18px] md:gap-y-6" :class="{ 'opacity-50': refreshing }">
        <SeriesTile v-for="item in visible" :key="item.series.id" :series="item.series">
          <RunStrip :run="item.run" />
          <span class="truncate text-[13px] font-extrabold text-white">{{ item.missing_count === 1 ? "1 issue away" : `${item.missing_count} to go` }}</span>
          <span class="truncate text-xs font-semibold text-slate-400">Next #{{ item.next_missing }} · {{ item.series.owned_count }} of {{ item.series.issue_count }} owned</span>
          <span class="truncate text-xs font-semibold text-slate-400">{{ item.caught_up ? "Read everything you own" : `${item.unread_on_shelf} unread on the shelf` }}</span>
        </SeriesTile>
      </ul>
      <div v-if="items.length > LIMIT" class="mt-4">
        <button class="text-sm font-bold text-sky-400 hover:text-sky-300" type="button" :aria-expanded="expanded" @click="expanded = !expanded">
          {{ expanded ? "Show fewer" : `Show all ${items.length}` }}
        </button>
      </div>
    </template>

    <p v-else class="py-6 text-slate-400">
      Every run you've started is complete.
      <RouterLink to="/series/create" class="font-bold text-sky-400 hover:text-sky-300">Add series</RouterLink>
    </p>

    <p v-if="unstarted && unstarted.count" class="mt-3.5 text-[13px] font-semibold text-slate-400">
      {{ unstarted.count }} series {{ unstarted.count === 1 ? "has" : "have" }} nothing bought yet: {{ unstartedNames }}.
      <RouterLink to="/collection" class="font-bold text-sky-400 hover:text-sky-300">Open collection</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import SectionHead from "./SectionHead.vue";
import SeriesTile from "./SeriesTile.vue";
import RunStrip from "./RunStrip.vue";
import Skeleton from "./Skeleton.vue";

const LIMIT = 8;
const { data, loading, refreshing, error, reload } = useInsightsSection(() => InsightsService.getGetNext());
const expanded = ref(false);
const sort = ref<"closest" | "recent">("closest");

const items = computed(() => {
  const rows = data.value?.items ?? [];
  if (sort.value === "closest") return rows;
  return [...rows].sort((a, b) => (b.last_bought ?? "").localeCompare(a.last_bought ?? "") || a.missing_count - b.missing_count);
});
const visible = computed(() => (expanded.value ? items.value : items.value.slice(0, LIMIT)));
const unstarted = computed(() => data.value?.unstarted ?? null);

const subtitle = computed(() => {
  if (!data.value) return "";
  const { one_away, items: rows } = data.value;
  if (one_away) return `${one_away} series one issue away`;
  return rows.length ? `${rows.length} runs to finish` : "";
});

const unstartedNames = computed(() => {
  const u = unstarted.value;
  if (!u) return "";
  const rest = u.count - u.titles.length;
  return rest > 0 ? `${u.titles.join(", ")} and ${rest} more` : u.titles.join(", ");
});
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
