<template>
  <div class="flex h-full flex-col">
    <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-2">
      <h2 class="text-xl font-extrabold text-[#F9FAFB]">{{ title }}</h2>
      <slot name="aside" />
    </div>
    <div class="mt-3 flex flex-wrap gap-2">
      <SegmentedControl v-model="field" :options="FIELDS" label="Group by" />
      <SegmentedControl v-model="type" :options="TYPES" label="Count" />
    </div>

    <p v-if="loading && !slices.length" class="mt-6 text-slate-400">Loading…</p>
    <p v-else-if="!slices.length" class="mt-6 text-slate-400">No data available to display</p>

    <div v-else class="mt-2 flex flex-1 flex-col" :class="{ 'opacity-50': loading }">
      <!-- donut and legend sit centred in whatever height the panel has; the summary stays on the baseline -->
      <div class="flex flex-1 flex-col items-center justify-center gap-4 py-2">
      <!-- the donut, with the readout sitting in its hole -->
      <div class="relative h-[260px] w-full max-w-[300px]" role="img" :aria-label="summary">
        <v-chart ref="chart" :option="option" :autoresize="true" class="h-full w-full"
          @mouseover="onSliceEnter" @mouseout="onSliceLeave" @click="onSliceClick" />
        <div class="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div class="flex w-[136px] flex-col items-center text-center">
          <template v-if="focused">
            <span class="w-full truncate text-sm font-extrabold text-white" :title="focused.name">{{ focused.name }}</span>
            <span class="mt-0.5 text-[26px] font-black leading-none tracking-tight text-white tabular-nums">{{ focused.value }}</span>
            <span class="mt-1 text-xs font-bold text-slate-400">{{ share(focused.value) }} of {{ unit }}</span>
          </template>
          <template v-else>
            <span class="text-[30px] font-black leading-none tracking-tight text-white tabular-nums">{{ total }}</span>
            <span class="mt-1 text-xs font-bold text-slate-400">{{ unit }}</span>
          </template>
          </div>
        </div>
      </div>

      <!-- legend, and the table view: every slice named, valued, and (for real entities) a link -->
      <ul class="grid w-full gap-x-6 gap-y-1.5 text-sm sm:grid-cols-2" aria-label="Breakdown">
        <li v-for="(slice, i) in slices" :key="slice.name">
          <component :is="slice.other ? 'div' : RouterLink" :to="slice.other ? undefined : filterRoute(slice.name)"
            class="legend-row" :class="{ 'legend-row--link': !slice.other, 'legend-row--dim': focused && focused.name !== slice.name }"
            :title="slice.other ? slice.members.join(', ') : `See ${slice.name} in your collection`"
            @mouseenter="highlight(i)" @mouseleave="downplay(i)">
            <span class="h-2.5 w-2.5 shrink-0 rounded-[3px]" :style="{ background: slice.color }" aria-hidden="true"></span>
            <span class="min-w-0 flex-1 truncate font-bold text-slate-300">{{ slice.name }}</span>
            <span class="tabular-nums font-extrabold text-white">{{ slice.value }}</span>
            <span class="w-9 text-right tabular-nums text-xs font-bold text-slate-500">{{ share(slice.value) }}</span>
          </component>
        </li>
      </ul>
      </div>

      <p class="w-full pt-4 text-[13px] font-semibold text-slate-400">{{ summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { use } from "echarts/core";
import { PieChart } from "echarts/charts";
import { SVGRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import { RouterLink, useRouter } from "vue-router";
import DashboardService from "@/services/DashboardService";
import SegmentedControl from "@/components/common/SegmentedControl.vue";

use([PieChart, SVGRenderer]);

const FIELDS = [
  { label: "Publisher", value: "publisher" },
  { label: "Genre", value: "genre" },
  { label: "Creator", value: "creator" },
  { label: "Character", value: "character" },
];
const TYPES = [
  { label: "Series", value: "series" },
  { label: "Issues", value: "issue" },
];
const LIMIT = 8;
// At most six segments read at a glance: the top five keep their own colour, the rest fold into Other.
const MAX_SLICES = 6;

// Five categorical slots (validated for this dark surface) in fixed order, plus a neutral for Other.
// Colour follows the entity: once a name has a slot it keeps it while the grouping stays the same.
const SLOTS = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"];
const OTHER_COLOR = "#94a3b8";
const SURFACE = "#131a2b";

interface Row { name: string; value: number }
interface Slice extends Row { color: string; other: boolean; members: string[] }

const router = useRouter();
const chart = ref<InstanceType<typeof VChart> | null>(null);
const field = ref("publisher");
const type = ref("series");
const rows = ref<Row[]>([]);
const loading = ref(false);
const focused = ref<Row | null>(null);
const slotByName = new Map<string, string>();

const unit = computed(() => (type.value === "series" ? "series" : "issues"));
const title = computed(() => `${type.value === "series" ? "Series" : "Issues"} by ${field.value}`);
const total = computed(() => rows.value.reduce((s, r) => s + r.value, 0));

function colorFor(name: string) {
  if (!slotByName.has(name)) slotByName.set(name, SLOTS[slotByName.size % SLOTS.length]);
  return slotByName.get(name)!;
}

const slices = computed<Slice[]>(() => {
  const sorted = [...rows.value].sort((a, b) => b.value - a.value);
  if (sorted.length <= MAX_SLICES) {
    return sorted.map((r) => ({ ...r, color: colorFor(r.name), other: false, members: [] }));
  }
  const kept = sorted.slice(0, MAX_SLICES - 1);
  const rest = sorted.slice(MAX_SLICES - 1);
  return [
    ...kept.map((r) => ({ ...r, color: colorFor(r.name), other: false, members: [] })),
    { name: "Other", value: rest.reduce((s, r) => s + r.value, 0), color: OTHER_COLOR, other: true, members: rest.map((r) => r.name) },
  ];
});

function share(value: number) {
  return total.value ? `${Math.round((100 * value) / total.value)}%` : "0%";
}

const summary = computed(() => {
  if (!rows.value.length) return "";
  const lead = slices.value[0];
  const scope = rows.value.length === 1 ? "" : ` across the top ${rows.value.length} ${field.value}s`;
  return `${lead.name} leads with ${lead.value} of ${total.value} ${unit.value} (${share(lead.value)})${scope}.`;
});

function filterRoute(name: string) {
  return { path: "/collection", query: { [field.value]: name } };
}

const option = computed(() => ({
  backgroundColor: "transparent",
  animationDuration: 500,
  animationEasing: "cubicOut",
  series: [
    {
      type: "pie",
      radius: ["63%", "92%"],
      center: ["50%", "50%"],
      startAngle: 90,
      avoidLabelOverlap: false,
      label: { show: false },
      labelLine: { show: false },
      itemStyle: { borderColor: SURFACE, borderWidth: 2, borderRadius: 4 },
      emphasis: { scale: true, scaleSize: 5, focus: "self", itemStyle: { borderColor: SURFACE } },
      blur: { itemStyle: { opacity: 0.3 } },
      data: slices.value.map((s) => ({ name: s.name, value: s.value, itemStyle: { color: s.color } })),
    },
  ],
}));

function onSliceEnter(params: any) {
  const slice = slices.value[params.dataIndex];
  if (slice) focused.value = { name: slice.name, value: slice.value };
}
function onSliceLeave() {
  focused.value = null;
}
function onSliceClick(params: any) {
  const slice = slices.value[params.dataIndex];
  if (slice && !slice.other) router.push(filterRoute(slice.name));
}

function highlight(dataIndex: number) {
  chart.value?.dispatchAction({ type: "highlight", seriesIndex: 0, dataIndex });
  onSliceEnter({ dataIndex });
}
function downplay(dataIndex: number) {
  chart.value?.dispatchAction({ type: "downplay", seriesIndex: 0, dataIndex });
  onSliceLeave();
}

async function load() {
  loading.value = true;
  try {
    const response = await DashboardService.getUserFieldCount(field.value, type.value, LIMIT);
    rows.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
    focused.value = null;
  }
}

watch(field, () => slotByName.clear());
watch([field, type], load, { immediate: true });
</script>

<style scoped>
.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
  padding: 0 6px;
  margin: 0 -6px;
  border-radius: 6px;
  transition: background-color 0.12s ease, opacity 0.12s ease;
}
.legend-row--link:hover {
  background: rgba(255, 255, 255, 0.05);
}
.legend-row--link:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}
.legend-row--dim {
  opacity: 0.45;
}
</style>
