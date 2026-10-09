<template>
  <span class="inline-flex items-end gap-[3px]" role="img" :aria-label="summary">
    <i
      v-for="tick in shown"
      :key="tick.number"
      :title="`#${tick.number} · ${NAMES[tick.state]}`"
      class="block w-2 rounded-[2px]"
      :class="CLASSES[tick.state]"
    ></i>
    <span v-if="run.length > max" class="ml-0.5 text-[11px] font-bold text-slate-500">+{{ run.length - max }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { RunState, RunTick } from "@/types/insights.types";

const props = withDefaults(defineProps<{ run: RunTick[]; max?: number }>(), { max: 14 });

const NAMES: Record<RunState, string> = {
  read: "read",
  owned: "owned, unread",
  missing: "not owned",
};

const CLASSES: Record<RunState, string> = {
  read: "h-3.5 bg-green-400",
  owned: "h-3.5 border-[1.5px] border-sky-500 bg-sky-500/10",
  missing: "h-3.5 bg-red-900",
};

const shown = computed(() => props.run.slice(0, props.max));
const summary = computed(() => {
  const count = (state: RunState) => props.run.filter((t) => t.state === state).length;
  return `${count("read")} read, ${count("owned")} unread on the shelf, ${count("missing")} not owned`;
});
</script>
