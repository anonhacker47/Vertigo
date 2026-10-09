<template>
  <div>
    <div class="flex items-baseline justify-between gap-3">
      <p class="text-base font-bold text-white">Bought vs read by {{ mode }}</p>
      <button class="text-[13px] font-bold text-sky-400 hover:text-sky-300" type="button" :aria-pressed="tableView" @click="tableView = !tableView">
        {{ tableView ? "Chart view" : "Table view" }}
      </button>
    </div>

    <table v-if="tableView" class="mt-2.5 w-full border-collapse text-sm tabular-nums">
      <thead>
        <tr class="text-left text-[13px] font-bold text-slate-400">
          <th class="border-b border-slate-700 px-2 py-1.5" scope="col">Period</th>
          <th class="border-b border-slate-700 px-2 py-1.5 text-right" scope="col">Bought</th>
          <th class="border-b border-slate-700 px-2 py-1.5 text-right" scope="col">Read</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in buckets" :key="b.key" class="text-slate-300">
          <td class="border-b border-white/8 px-2 py-1.5">{{ b.label }}</td>
          <td class="border-b border-white/8 px-2 py-1.5 text-right">{{ b.bought }}</td>
          <td class="border-b border-white/8 px-2 py-1.5 text-right">{{ b.read }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else class="mt-2.5 h-55 md:h-65" role="img" :aria-label="summary">
      <v-chart :option="option" :autoresize="true" class="h-full w-full" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { use } from "echarts/core";
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import type { ActivityBucket } from "@/types/insights.types";

use([BarChart, GridComponent, LegendComponent, TooltipComponent, SVGRenderer]);

const props = defineProps<{ buckets: ActivityBucket[]; mode: "month" | "year" }>();
const tableView = ref(false);

const BOUGHT = "#0369a1"; 
const READ = "#16a34a"; 
const FONT = "Nunito, ui-sans-serif, system-ui, sans-serif";

function lastMaxIndex(values: number[]): number {
  const max = Math.max(...values);
  let idx = -1;
  values.forEach((v, i) => { if (v === max) idx = i; });
  return max > 0 ? idx : -1;
}

function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c] as string);
}

const summary = computed(() => {
  const b = props.buckets.reduce((s, x) => s + x.bought, 0);
  const r = props.buckets.reduce((s, x) => s + x.read, 0);
  return `Bought vs read by ${props.mode}: ${b} bought, ${r} read across ${props.buckets.length} ${props.mode}s.`;
});

const option = computed(() => {
  const labels = props.buckets.map((b) => (props.mode === "month" ? b.label.slice(0, 3) : b.label));
  const bought = props.buckets.map((b) => b.bought);
  const read = props.buckets.map((b) => b.read);
  const maxBought = lastMaxIndex(bought);
  const maxRead = lastMaxIndex(read);
  const labelStyle = { color: "#cbd5e1", fontFamily: FONT, fontSize: 11, fontWeight: 800 };
  return {
    backgroundColor: "transparent",
    animationDuration: 400,
    grid: { left: 36, right: 8, top: 28, bottom: 52, containLabel: false },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow", shadowStyle: { color: "rgba(255,255,255,.05)" } },
      backgroundColor: "#0b1220",
      borderColor: "#334155",
      textStyle: { color: "#cbd5e1", fontFamily: FONT, fontSize: 13 },
      formatter: (params: any[]) => {
        const full = props.buckets[params[0]?.dataIndex]?.label ?? "";
        const rows = params
          .map((p) => `<div style="display:flex;align-items:center;gap:8px"><span style="display:inline-block;width:14px;height:3px;border-radius:2px;background:${p.color}"></span><strong style="color:#fff">${p.value}</strong><span>${escapeHtml(String(p.seriesName))}</span></div>`)
          .join("");
        return `<b style="display:block;color:#fff;margin-bottom:4px">${escapeHtml(full)}</b>${rows}`;
      },
    },
    legend: {
      bottom: 0,
      left: 0,
      icon: "roundRect",
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { color: "#94a3b8", fontFamily: FONT, fontSize: 13, fontWeight: 600 },
    },
    xAxis: {
      type: "category",
      data: labels,
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
        name: "Bought",
        type: "bar",
        data: bought,
        barMaxWidth: 24,
        barGap: "10%",
        itemStyle: { color: BOUGHT, borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: "top", ...labelStyle, formatter: (p: any) => (p.dataIndex === maxBought ? String(p.value) : "") },
      },
      {
        name: "Read",
        type: "bar",
        data: read,
        barMaxWidth: 24,
        itemStyle: { color: READ, borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: "top", ...labelStyle, formatter: (p: any) => (p.dataIndex === maxRead ? String(p.value) : "") },
      },
    ],
  };
});
</script>
