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

    <p v-if="loading && !rows.length" class="mt-6 text-slate-400">Loading…</p>
    <p v-else-if="!rows.length" class="mt-6 text-slate-400">No data available to display</p>
    <ol v-else class="mt-5 flex flex-col gap-2.5" :class="{ 'opacity-50': loading }">
      <li v-for="(row, i) in rows" :key="row.name" class="grid grid-cols-[minmax(0,10rem)_1fr_auto] items-center gap-3 text-sm">
        <span class="truncate font-bold text-slate-300" :title="row.name">{{ row.name }}</span>
        <div class="h-2.5 rounded-[3px] bg-white/[.05]">
          <div class="h-full rounded-[3px]" :class="i === 0 ? 'bg-sky-500' : 'bg-sky-700'" :style="{ width: `${(100 * row.value) / max}%` }"></div>
        </div>
        <span class="min-w-[2ch] text-right font-extrabold tabular-nums text-white">{{ row.value }}</span>
      </li>
    </ol>
    <p v-if="rows.length" class="mt-auto pt-4 text-[13px] font-semibold text-slate-400">
      Top {{ rows.length }}. {{ rows[0].name }} leads with {{ rows[0].value }} of {{ total }}.
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import DashboardService from "@/services/DashboardService";
import SegmentedControl from "@/components/common/SegmentedControl.vue";

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

const field = ref("publisher");
const type = ref("series");
const rows = ref<{ name: string; value: number }[]>([]);
const loading = ref(false);

const title = computed(() => `${type.value === "series" ? "Series" : "Issues"} by ${field.value}`);
const max = computed(() => Math.max(1, ...rows.value.map((r) => r.value)));
const total = computed(() => rows.value.reduce((s, r) => s + r.value, 0));

async function load() {
  loading.value = true;
  try {
    const response = await DashboardService.getUserFieldCount(field.value, type.value, LIMIT);
    rows.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

watch([field, type], load, { immediate: true });
</script>
