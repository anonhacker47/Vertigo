<template>
  <div class="transfer-progress" :class="`transfer-progress--${run.status}`" role="status" aria-live="polite">
    <div class="flex items-center gap-3">
      <span class="transfer-progress__icon" aria-hidden="true">
        <i v-if="busy" class="pi pi-spin pi-sync"></i>
        <i v-else-if="run.status === 'done'" class="pi pi-check"></i>
        <i v-else class="pi pi-exclamation-triangle"></i>
      </span>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-semibold text-slate-100">{{ title }}</p>
        <p class="text-xs leading-relaxed text-slate-400">{{ detail }}</p>
        <slot />
      </div>
      <Button v-if="!busy" type="button" :label="dismissLabel" size="small" text severity="secondary"
        @click="emit('dismiss')" />
    </div>
    <ProgressBar v-if="busy" :value="percent" :mode="run.total ? 'determinate' : 'indeterminate'"
      :showValue="false" class="mt-3" style="height: 6px" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Button from "primevue/button";
import ProgressBar from "primevue/progressbar";
import type { TransferRun } from "@/types/transfer.types";

const props = withDefaults(defineProps<{
  run: TransferRun;
  percent: number;
  /** One line describing what was done, shown when the run finished. */
  result: string;
  busyTitle?: string;
  dismissLabel?: string;
}>(), { busyTitle: "Working", dismissLabel: "Dismiss" });

const emit = defineEmits<{ (e: "dismiss"): void }>();

const busy = computed(() => props.run.status === "queued" || props.run.status === "running");

const title = computed(() => {
  if (props.run.status === "queued") return "Waiting for a free worker";
  if (props.run.status === "running") return props.busyTitle;
  if (props.run.status === "done") return "Done";
  return "Couldn't finish";
});

const detail = computed(() => {
  if (busy.value) {
    return props.run.total
      ? `${props.run.done.toLocaleString()} of ${props.run.total.toLocaleString()}`
      : props.run.label;
  }
  if (props.run.status === "done") return props.result;
  return props.run.error || "Something went wrong on the server.";
});
</script>

<style scoped>
.transfer-progress {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(2, 6, 23, 0.35);
}
.transfer-progress__icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex: none;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  font-size: 13px;
}
.transfer-progress--done {
  border-color: rgba(74, 222, 128, 0.25);
}
.transfer-progress--done .transfer-progress__icon {
  background: rgba(74, 222, 128, 0.12);
  color: #4ade80;
}
.transfer-progress--failed {
  border-color: rgba(248, 113, 113, 0.3);
}
.transfer-progress--failed .transfer-progress__icon {
  background: rgba(248, 113, 113, 0.12);
  color: #f87171;
}
</style>
