<template>
  <div v-if="jobs.length" ref="root" class="relative">
    <button type="button" class="nav-icon" :class="{ 'nav-icon--on': open }" :aria-expanded="open" aria-haspopup="true"
      :aria-label="label" :title="label" @click="open = !open">
      <i class="pi pi-sync pi-spin text-sky-300"></i>
      <span class="badge">{{ jobs.length }}</span>
    </button>

    <div v-if="open" class="panel" role="dialog" aria-label="Background jobs">
      <div class="panel__list">
        <JobRow v-for="job in jobs" :key="job.id" :job="job" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useJobs } from "@/composables/useJobs";
import JobRow from "./JobRow.vue";

const { jobs, running, queued } = useJobs();

const root = ref<HTMLElement | null>(null);
const open = ref(false);
const route = useRoute();

const label = computed(() => {
  const parts = [running.value ? `${running.value} running` : "", queued.value ? `${queued.value} waiting` : ""];
  return `Background jobs: ${parts.filter(Boolean).join(", ")}`;
});

function onDocumentClick(event: MouseEvent) {
  if (open.value && root.value && !root.value.contains(event.target as Node)) open.value = false;
}
function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") open.value = false;
}
onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKey);
});
watch(() => route.fullPath, () => (open.value = false));
watch(() => jobs.value.length, (n) => {
  if (!n) open.value = false;
});
</script>

<style scoped>
.nav-icon {
  position: relative;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  color: #cbd5e1;
  font-size: 16px;
  transition: background-color 0.12s ease;
}
.nav-icon:hover,
.nav-icon--on { background: rgba(255, 255, 255, 0.08); }
.nav-icon:focus-visible { outline: 2px solid #38bdf8; outline-offset: 2px; }
.badge {
  position: absolute;
  top: 4px;
  right: 2px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  border-radius: 999px;
  background: #38bdf8;
  color: #0b1220;
  font-size: 11px;
  font-weight: 800;
  line-height: 17px;
  text-align: center;
}
.panel {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  z-index: 60;
  width: min(20rem, calc(100vw - 2.5rem));
  padding: 6px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(11, 18, 32, 0.98);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55);
}
.panel__list { max-height: 24rem; overflow-y: auto; }
</style>
