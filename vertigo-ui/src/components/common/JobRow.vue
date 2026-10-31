<template>
  <div class="jobrow" :class="`jobrow--${job.status}`">
    <span class="jobrow__state" aria-hidden="true">
      <i v-if="job.status === 'running'" class="pi pi-spin pi-sync"></i>
      <i v-else class="pi pi-clock"></i>
    </span>
    <span class="min-w-0 flex-1">
      <span class="jobrow__label">{{ job.label }}</span>
      <span class="jobrow__meta">{{ job.status === "running" ? "Running" : "Waiting" }}</span>
    </span>
  </div>
</template>

<script setup lang="ts">
import type { Job } from "@/types/jobs.types";

defineProps<{ job: Job }>();
</script>

<style scoped>
.jobrow {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  border-radius: 10px;
}
.jobrow__state {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  flex: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  font-size: 12px;
}
.jobrow--running .jobrow__state { color: #38bdf8; background: rgba(56, 189, 248, 0.12); }
.jobrow__label,
.jobrow__meta {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.jobrow__label { color: #fff; font-size: 13.5px; font-weight: 700; }
.jobrow__meta { color: #94a3b8; font-size: 12px; font-weight: 600; }
</style>
