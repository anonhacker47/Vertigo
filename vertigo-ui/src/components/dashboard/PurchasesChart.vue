<template>
  <div class="flex h-full flex-col">
    <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-2">
      <h2 class="text-xl font-extrabold text-[#F9FAFB]">Purchases in {{ year }}</h2>
      <select v-model.number="year" class="year-select" aria-label="Year">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <div class="mt-3 flex items-baseline gap-2">
      <span class="text-[32px] font-black leading-none tracking-tight text-white"><AnimatedNumber :number="bought" /></span>
      <span class="text-sm font-semibold text-slate-400">{{ bought === 1 ? "book bought" : "books bought" }}</span>
    </div>

    <div class="mt-3 min-h-[200px] flex-1" :class="{ 'opacity-50': loading }" role="img" :aria-label="summary">
      <v-chart v-if="hasData" :option="option" :autoresize="true" class="h-full w-full" />
      <p v-else class="pt-8 text-center text-slate-400">No purchase data available to display</p>
    </div>
    <p v-if="hasData" class="mt-2 text-[13px] font-semibold text-slate-400">{{ summary }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { use } from "echarts/core";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import DashboardService from "@/services/DashboardService";
import AnimatedNumber from "@/components/common/AnimatedNumber.vue";

use([BarChart, GridComponent, TooltipComponent, SVGRenderer]);

const props = defineProps<{ currencySymbol: string }>();

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const FONT = "Nunito, ui-sans-serif, system-ui, sans-serif";
const thisYear = new Date().getFullYear();
const years = Array.from({ length: 8 }, (_, i) => thisYear - i);

const year = ref(thisYear);
const counts = ref<number[]>(Array(12).fill(0));
const spent = ref<number[]>(Array(12).fill(0));
const loading = ref(false);

const bought = computed(() => counts.value.reduce((s, n) => s + n, 0));
const hasData = computed(() => bought.value > 0);
const maxIndex = computed(() => {
  const max = Math.max(...counts.value);
  let idx = -1;
  counts.value.forEach((v, i) => { if (v === max && v > 0) idx = i; });
  return idx;
});
const summary = computed(() => {
  if (!hasData.value) return `No purchases logged in ${year.value}.`;
  const total = spent.value.reduce((s, n) => s + n, 0);
  const average = total > 0 ? `${props.currencySymbol}${Math.round(total / bought.value).toLocaleString()}` : null;
  const best = `${MONTHS[maxIndex.value]} was the biggest month with ${counts.value[maxIndex.value]}.`;
  return average ? `${best} Average ${average} a book.` : best;
});

function money(value: number): string {
  return `${props.currencySymbol}${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

const option = computed(() => ({
  backgroundColor: "transparent",
  animationDuration: 400,
  grid: { left: 30, right: 6, top: 24, bottom: 26 },
  tooltip: {
    trigger: "axis",
    axisPointer: { type: "shadow", shadowStyle: { color: "rgba(255,255,255,.05)" } },
    backgroundColor: "#0b1220",
    borderColor: "#334155",
    textStyle: { color: "#cbd5e1", fontFamily: FONT, fontSize: 13 },
    formatter: (params: any[]) => {
      const i = params[0]?.dataIndex ?? 0;
      const n = counts.value[i];
      return `<b style="color:#fff">${MONTHS[i]} ${year.value}</b><br/>${n} ${n === 1 ? "book" : "books"}<br/>Spent: ${money(spent.value[i])}`;
    },
  },
  xAxis: {
    type: "category",
    data: MONTHS,
    axisLine: { lineStyle: { color: "#334155" } },
    axisTick: { show: false },
    axisLabel: { color: "#94a3b8", fontFamily: FONT, fontSize: 11, fontWeight: 700 },
  },
  yAxis: {
    type: "value",
    minInterval: 1,
    splitLine: { lineStyle: { color: "#1e293b", type: "solid" } },
    axisLabel: { color: "#64748b", fontFamily: FONT, fontSize: 11, fontWeight: 700 },
  },
  series: [
    {
      type: "bar",
      data: counts.value.map((v, i) => ({ value: v, itemStyle: { color: i === maxIndex.value ? "#0ea5e9" : "#0369a1", borderRadius: [4, 4, 0, 0] } })),
      barMaxWidth: 24,
      label: {
        show: true,
        position: "top",
        color: "#cbd5e1",
        fontFamily: FONT,
        fontSize: 11,
        fontWeight: 800,
        formatter: (p: any) => (p.dataIndex === maxIndex.value ? String(p.value) : ""),
      },
    },
  ],
}));

async function load() {
  loading.value = true;
  try {
    const response = await DashboardService.getPurchasesPerMonth(year.value);
    const byMonth = new Map<number, { count: number; spent: number }>();
    for (const row of response.data as { month: string; count: number; spent: number | null }[]) {
      byMonth.set(Number(row.month.slice(-2)), { count: row.count, spent: row.spent ?? 0 });
    }
    counts.value = MONTHS.map((_, i) => byMonth.get(i + 1)?.count ?? 0);
    spent.value = MONTHS.map((_, i) => byMonth.get(i + 1)?.spent ?? 0);
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

watch(year, load, { immediate: true });
</script>

<style scoped>
.year-select {
  appearance: none;
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  font: inherit;
  font-weight: 700;
  font-size: 13px;
  padding: 6px 30px 6px 12px;
  border-radius: 10px;
  background-image: linear-gradient(45deg, transparent 50%, #94a3b8 50%), linear-gradient(135deg, #94a3b8 50%, transparent 50%);
  background-position: calc(100% - 16px) 55%, calc(100% - 11px) 55%;
  background-size: 5px 5px;
  background-repeat: no-repeat;
}
.year-select:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
</style>
